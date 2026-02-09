import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout

# =========================
# ====== PARAMETERS ======
# =========================

API_KEY = "PUT_YOUR_GOLD_API_KEY_HERE"
BASE_URL = "https://www.gold-api.com/api/XAU/USD"

# Data settings
CANDLE_INTERVAL_MINUTES = 1          # timeframe (1 minute)
LOOKBACK_MINUTES = 60                # how many past minutes per sample
PREDICT_MINUTES_AHEAD = 3             # prediction horizon
TRAIN_UNTIL_MINUTES_AGO = 20          # stop data 20 minutes ago

# Trading settings
CAPITAL_USD = 1000                   # your capital
RISK_PERCENT = 0.02                  # risk per trade (2%)

# Neural Network settings
EPOCHS = 20
BATCH_SIZE = 32
LSTM_UNITS = 50
DROPOUT_RATE = 0.2

# =========================
# ===== DATA FETCH =======
# =========================

def fetch_current_price():
    r = requests.get(f"{BASE_URL}?apikey={API_KEY}")
    data = r.json()
    return float(data["price"])

def generate_historical_data():
    """
    Gold-API free does not provide historical candles,
    so we simulate minute candles using repeated pulls.
    This is for AI structure/testing purposes.
    """
    end_time = datetime.utcnow() - timedelta(minutes=TRAIN_UNTIL_MINUTES_AGO)
    start_time = end_time - timedelta(days=30)

    prices = []
    timestamps = []

    current_time = start_time
    last_price = fetch_current_price()

    while current_time <= end_time:
        # simulate micro-movement
        last_price += np.random.normal(0, 0.15)
        prices.append(last_price)
        timestamps.append(current_time)
        current_time += timedelta(minutes=1)

    df = pd.DataFrame({
        "time": timestamps,
        "price": prices
    })

    return df

# =========================
# ===== FEATURE BUILD ====
# =========================

def build_features(df):
    df["return"] = df["price"].pct_change()
    df["ma_5"] = df["price"].rolling(5).mean()
    df["ma_20"] = df["price"].rolling(20).mean()
    df["volatility"] = df["return"].rolling(10).std()
    df.dropna(inplace=True)
    return df

# =========================
# ===== DATA PREP ========
# =========================

def prepare_lstm_data(df):
    features = ["price", "return", "ma_5", "ma_20", "volatility"]
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[features])

    X, y = [], []

    for i in range(LOOKBACK_MINUTES, len(scaled) - PREDICT_MINUTES_AHEAD):
        X.append(scaled[i - LOOKBACK_MINUTES:i])
        future_price = df["price"].iloc[i + PREDICT_MINUTES_AHEAD]
        current_price = df["price"].iloc[i]
        y.append((future_price - current_price) / current_price)

    return np.array(X), np.array(y), scaler

# =========================
# ===== MODEL ============
# =========================

def build_model(input_shape):
    model = Sequential([
        LSTM(LSTM_UNITS, return_sequences=True, input_shape=input_shape),
        Dropout(DROPOUT_RATE),
        LSTM(LSTM_UNITS),
        Dropout(DROPOUT_RATE),
        Dense(1, activation="tanh")
    ])
    model.compile(optimizer="adam", loss="mse")
    return model

# =========================
# ===== PREDICTION =======
# =========================

def make_decision(predicted_return):
    direction = "BUY" if predicted_return > 0 else "SELL"
    expected_move_pct = abs(predicted_return) * 100

    risk_amount = CAPITAL_USD * RISK_PERCENT
    expected_profit = risk_amount * (expected_move_pct / 0.2)

    wait_time_minutes = PREDICT_MINUTES_AHEAD

    return {
        "direction": direction,
        "expected_move_pct": round(expected_move_pct, 3),
        "expected_profit_usd": round(expected_profit, 2),
        "wait_time_minutes": wait_time_minutes
    }

# =========================
# ===== MAIN =============
# =========================

def main():
    print("Fetching & building data...")
    df = generate_historical_data()
    df = build_features(df)

    X, y, scaler = prepare_lstm_data(df)

    model = build_model((X.shape[1], X.shape[2]))
    model.fit(X, y, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=0)

    last_sequence = X[-1].reshape(1, X.shape[1], X.shape[2])
    predicted_return = model.predict(last_sequence)[0][0]

    decision = make_decision(predicted_return)

    print("\n===== AI TRADE DECISION =====")
    print(f"Action            : {decision['direction']}")
    print(f"Expected Move     : {decision['expected_move_pct']} %")
    print(f"Expected Profit   : ${decision['expected_profit_usd']}")
    print(f"Estimated Wait    : {decision['wait_time_minutes']} minutes")

if __name__ == "__main__":
    main()
