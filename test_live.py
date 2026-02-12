import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import joblib
from datetime import datetime, timedelta

# ===========================
# 1. CALIBRATION (NEW!)
# ===========================
# IF THE BOT PRICE IS WRONG, ENTER YOUR BROKER'S PRICE HERE.
# Set to 0 to disable calibration.
YOUR_BROKER_PRICE = 4915.00  # <--- UPDATE THIS if needed

# ===========================
# 2. CONFIGURATION
# ===========================
import dukascopy_python as dp
import dukascopy_python.instruments as instruments

INSTRUMENT = instruments.INSTRUMENT_FX_METALS_XAU_USD 
INTERVAL_TICKS = dp.INTERVAL_TICK
OFFER_SIDE = dp.OFFER_SIDE_ASK

# Model Config
SEQ_LEN = 64
MODEL_PATH = "lstm_xauusd.pt"
SCALER_PATH = "scaler_xauusd.pkl"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ===========================
# 3. MODEL DEFINITION
# ===========================
class LSTMModel(nn.Module):
    def __init__(self, input_size=5, hidden_size=64, num_layers=2, output_size=4):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

# ===========================
# 4. HELPER FUNCTIONS
# ===========================
def load_resources():
    print("Loading resources...")
    try:
        scaler = joblib.load(SCALER_PATH)
        model = LSTMModel().to(DEVICE)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model.eval()
        return model, scaler
    except Exception as e:
        print(f"❌ Error loading resources: {e}")
        return None, None

def inverse_normalize(scaler, pred):
    dummy = np.zeros((1, 5))
    dummy[0, :4] = pred
    inv = scaler.inverse_transform(dummy)
    return inv[0, :4]

def get_live_data_from_ticks(minutes=180):
    print(f"Fetching REAL-TIME ticks for XAU/USD (Last {minutes} mins)...")
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(minutes=minutes)

    try:
        # Fetch RAW TICKS
        df_ticks = dp.fetch(
            instrument=INSTRUMENT,
            interval=INTERVAL_TICKS,
            start=start_date,
            end=end_date,
            offer_side=OFFER_SIDE
        )
        
        if df_ticks is None or df_ticks.empty:
            print("❌ Error: No tick data received.")
            return None, 0

        # --- FIX: ROBUST TIMESTAMP HANDLING ---
        if 'timestamp' in df_ticks.columns:
            df_ticks['timestamp'] = pd.to_datetime(df_ticks['timestamp'])
            df_ticks.set_index('timestamp', inplace=True)
        elif 'Timestamp' in df_ticks.columns:
            df_ticks['Timestamp'] = pd.to_datetime(df_ticks['Timestamp'])
            df_ticks.set_index('Timestamp', inplace=True)
        elif not isinstance(df_ticks.index, pd.DatetimeIndex):
            return None, 0

        # --- FIX: COLUMN NAMES ---
        df_ticks.columns = [c.lower() for c in df_ticks.columns]

        # Identify Price & Volume Columns
        price_col = 'ask' if 'ask' in df_ticks.columns else 'close'
        if price_col not in df_ticks.columns: price_col = df_ticks.columns[0]
        
        vol_col = 'ask_volume' if 'ask_volume' in df_ticks.columns else 'volume'

        # --- RESAMPLE TO 1-MINUTE CANDLES ---
        df_ohlc = df_ticks[price_col].resample('1min').ohlc()
        
        if vol_col and vol_col in df_ticks.columns:
            df_vol = df_ticks[vol_col].resample('1min').sum()
        else:
            df_vol = pd.Series(0, index=df_ohlc.index)

        df_candles = pd.concat([df_ohlc, df_vol], axis=1)
        df_candles.columns = ['open', 'high', 'low', 'close', 'volume']
        df_candles.dropna(inplace=True)
        
        # Get REAL-TIME price (Last tick)
        last_real_price = df_ticks[price_col].iloc[-1]
        
        return df_candles, last_real_price

    except Exception as e:
        print(f"❌ Error processing ticks: {e}")
        return None, 0

# ===========================
# 5. MAIN PREDICTION LOOP
# ===========================
def run_live_prediction():
    model, scaler = load_resources()
    if model is None: return

    # Fetch Data
    df, real_price_dukascopy = get_live_data_from_ticks(minutes=180) 
    if df is None: return
    
    if len(df) < SEQ_LEN:
        print(f"❌ Not enough history. Need {SEQ_LEN} candles, generated {len(df)}.")
        return

    # --- CALCULATION OF OFFSET ---
    # If user provided a price, calculate the difference
    offset = 0
    if YOUR_BROKER_PRICE > 0:
        offset = YOUR_BROKER_PRICE - real_price_dukascopy
        print(f"⚠️ Calibrating Price: Dukascopy ({real_price_dukascopy:.2f}) -> Your Broker ({YOUR_BROKER_PRICE:.2f})")
        print(f"   Offset Applied: {offset:+.2f}")

    real_price_calibrated = real_price_dukascopy + offset

    # --- PREDICTION ---
    current_window = df.values[-SEQ_LEN:] 
    future_predictions = []
    simulation_window = current_window.copy()

    print("\nCalculating next 3 minutes...")
    with torch.no_grad():
        for step in range(3):
            try:
                scaled_window = scaler.transform(simulation_window)
            except ValueError as e:
                print(f"❌ Scaler Error: {e}")
                return

            seq_tensor = torch.tensor(scaled_window, dtype=torch.float32).unsqueeze(0).to(DEVICE)
            pred_norm = model(seq_tensor) 
            pred_ohlc = inverse_normalize(scaler, pred_norm.cpu().numpy()[0])
            
            # Get raw prediction
            raw_pred_close = pred_ohlc[3]
            
            # Apply offset for display ONLY (don't feed offset back into model)
            future_predictions.append(raw_pred_close + offset)

            # Update Window (Use RAW values for model logic)
            last_volume = simulation_window[-1, 4] 
            new_row = np.array([pred_ohlc[0], pred_ohlc[1], pred_ohlc[2], raw_pred_close, last_volume])
            simulation_window = np.vstack([simulation_window[1:], new_row])

    # --- RESULTS ---
    avg_future_price = np.mean(future_predictions)
    
    # Calculate change percentage (Relative change is same regardless of offset)
    change = (avg_future_price - real_price_calibrated) / real_price_calibrated
    threshold = 0.001

    print("\n" + "=" * 40)
    print(f"TIMESTAMP (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 40)
    print(f"CURRENT PRICE:      {real_price_calibrated:.2f}")
    print("-" * 40)
    print(f"Next 1 Minute:      {future_predictions[0]:.2f}")
    print(f"Next 2 Minutes:     {future_predictions[1]:.2f}")
    print(f"Next 3 Minutes:     {future_predictions[2]:.2f}")
    print("-" * 40)
    print(f"Avg Future Price:   {avg_future_price:.2f}")
    print(f"Projected Change:   {change*100:.4f}%")
    print("=" * 40)

    if change > threshold:
        print(f"🚀 SIGNAL: BUY")
    elif change < -threshold:
        print(f"🔻 SIGNAL: SELL")
    else:
        print(f"⚪ SIGNAL: HOLD")

if __name__ == "__main__":
    run_live_prediction()
