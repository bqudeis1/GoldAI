import time
import json
import torch
import pandas as pd
import joblib
import warnings
import yfinance as yf
import os
from datetime import datetime
from model_defs import TradingTransformer
from huggingface_hub import upload_file

# ===========================
# 1. CONFIGURATION
# ===========================
warnings.filterwarnings("ignore")
SYMBOL = "GC=F" 
STATE_FILE = "/tmp/state.json"
REPO_ID = "bahaq/ks-data-storage" 
HF_TOKEN = os.environ.get("HF_TOKEN")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# AI Parameters
SEQ_LEN = 64        # Minutes of history the AI needs to see
SENSITIVITY = 10.0  # Amplifies the AI's raw output
THRESHOLD = 0.003   # Signal trigger level (Adjust this if it trades too much/little)

SCALER_PATH = "backend/scaler_transformer.pkl"
MODEL_PATH = "backend/transformer_xauusd.pt"

# ===========================
# 2. HELPERS
# ===========================
def sync_to_cloud(filename):
    if not HF_TOKEN: return
    try:
        upload_file(path_or_fileobj=filename, path_in_repo=os.path.basename(filename),
                    repo_id=REPO_ID, repo_type="dataset", token=HF_TOKEN)
    except: pass

def update_dashboard(price, pred, status):
    # This JSON structure matches what your React frontend expects
    data = {
        "price": float(price or 0), 
        "prediction": float(pred or 0), 
        "status": str(status or "SCANNING..."),
        "timestamp": datetime.now().strftime('%H:%M:%S'),
        "ai_conviction": int(min(100, max(0, abs(pred or 0) * 100 * 5))) # Visual bar logic
    }
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

def get_live_data():
    try:
        # Get 2 days of data to ensure we have enough for the SEQ_LEN
        df = yf.download(tickers=SYMBOL, period="2d", interval="1m", progress=False)
        
        if df is None or df.empty: return None, 0
        
        # Flatten Multi-Index if present (The "Close, GC=F" fix)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Standardize column names
        df.columns = [str(c).lower() for c in df.columns]
        
        # Return history (for AI) and current live price
        return df.iloc[:-1].copy(), float(df['close'].iloc[-1])
    except: return None, 0

# ===========================
# 3. MAIN ENGINE
# ===========================
def run_engine():
    print(f"--- 🎯 KING SNIPER ENGINE STARTING [Target: {SYMBOL}] ---")
    
    # 1. Initial State Push
    update_dashboard(0.0, 0.0, "INITIALIZING_AI")
    sync_to_cloud(STATE_FILE)
    
    # 2. Load the Brains
    try:
        scaler = joblib.load(SCALER_PATH)
        model = TradingTransformer().to(DEVICE)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model.eval()
        print("✅ AI Model & Scaler Loaded Successfully.")
    except Exception as e:
        print(f"❌ Critical Load Error: {e}")
        return

    # 3. The Infinite Loop
    while True:
        df, current_price = get_live_data()
        
        # We need data AND enough rows (SEQ_LEN) to run the model
        if df is not None and not df.empty and len(df) >= SEQ_LEN:
            try:
                # A. PREPARE DATA
                input_data = df[['open','high','low','close','volume']].tail(SEQ_LEN)
                scaled_data = scaler.transform(input_data)
                
                # B. RUN INFERENCE
                tensor = torch.tensor(scaled_data, dtype=torch.float32).unsqueeze(0).to(DEVICE)
                
                with torch.no_grad():
                    raw_pred = model(tensor)[0, 0].item()
                    pred_strength = raw_pred * SENSITIVITY
                
                # C. DECIDE STATUS
                if pred_strength > THRESHOLD:
                    status = "BUY"
                elif pred_strength < -THRESHOLD:
                    status = "SELL"
                else:
                    status = "SCANNING..."

                # D. UPDATE FRONTEND
                update_dashboard(current_price, pred_strength, status)
                sync_to_cloud(STATE_FILE)
                
                print(f"[{datetime.now().strftime('%H:%M')}] ${current_price:.1f} | AI: {pred_strength:.4f} | Status: {status}")

            except Exception as e:
                print(f"⚠️ Inference Loop Error: {e}")
                # Fallback update so the dashboard doesn't freeze
                update_dashboard(current_price, 0.0, "DATA_ERROR")
                sync_to_cloud(STATE_FILE)
        
        else:
            # Not enough data yet
            msg = f"Gathering Data ({len(df) if df is not None else 0}/{SEQ_LEN})..."
            print(msg)
            update_dashboard(current_price, 0.0, "BUFFERING_DATA")
            sync_to_cloud(STATE_FILE)
            
        time.sleep(15)

if __name__ == "__main__":
    run_engine()