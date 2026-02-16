import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import joblib
import os
import time  # <--- Added for cooling down
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset
from model_defs import TradingTransformer  # Ensure model_defs.py has the Transformer class

# ===========================
# 1. CONFIGURATION
# ===========================
DATA_PATH = "Gold_Data_XAUUSD/train_data.parquet"
MODEL_SAVE_PATH = "transformer_xauusd.pt"
SCALER_SAVE_PATH = "scaler_transformer.pkl"

SEQ_LEN = 64            # Look back 64 minutes
PREDICT_AHEAD = 5       # Predict 5 minutes into the future
BATCH_SIZE = 256        # Safe for 8GB GPU
EPOCHS = 50             # Give it time to learn deep patterns
LR = 0.0001             # Slow and steady wins the race
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ===========================
# 2. DATA LOADING
# ===========================
def prepare_data():
    print(f"📂 Loading data from {DATA_PATH}...")
    
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: File not found at {DATA_PATH}")
        exit()

    # Load Parquet
    df = pd.read_parquet(DATA_PATH)
    
    # Ensure columns match (Case insensitive)
    df.columns = [str(c).lower() for c in df.columns]
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    
    # Check if columns exist
    for col in required_cols:
        if col not in df.columns:
            print(f"❌ Missing column: {col}")
            exit()
            
    df = df[required_cols].astype(float)
    
    # --- TARGET CREATION ---
    # We want to predict the % Return 5 minutes from now
    df['return'] = df['close'].pct_change()
    df['target'] = df['return'].shift(-PREDICT_AHEAD)
    df.dropna(inplace=True)

    print(f"📊 Data Loaded: {len(df)} rows. Scaling now...")

    # Scale Inputs (-1 to 1 is best for Transformers)
    scaler = MinMaxScaler(feature_range=(-1, 1))
    data_scaled = scaler.fit_transform(df[required_cols])
    
    # Save scaler for live trading
    joblib.dump(scaler, SCALER_SAVE_PATH)
    print(f"✅ Scaler saved to {SCALER_SAVE_PATH}")

    # Create Sequences
    X, y = [], []
    targets = df['target'].values
    
    # Using a stride of 1 to get maximum training examples
    # (If memory error occurs here, change stride to 5 or 10)
    for i in range(len(data_scaled) - SEQ_LEN):
        X.append(data_scaled[i:i+SEQ_LEN])
        # Transformer output is dim=4, so we broadcast target to match
        y.append([targets[i+SEQ_LEN]] * 4) 

    return np.array(X), np.array(y)

# ===========================
# 3. TRAINING LOOP
# ===========================
def train():
    try:
        X, y = prepare_data()
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        return

    # Convert to Tensor (Move to GPU later to save VRAM)
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)

    print(f"🧠 Training on {len(X)} sequences. Moving to GPU in batches...")

    dataset = TensorDataset(X_tensor, y_tensor)
    
    # Num_workers=0 is safer on Windows to avoid crashing
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, pin_memory=True)

    model = TradingTransformer().to(DEVICE)
    
    # HuberLoss is better than MSE for financial data because it ignores huge outlier spikes
    criterion = nn.HuberLoss() 
    
    # AdamW is the standard for Transformers (fixes weight decay)
    optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-5)
    
    # Scheduler: Reduce LR if loss stops improving (The "Fine-Tuning" phase)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3, factor=0.5)

    best_loss = float('inf')
    patience_counter = 0

    print(f"🚀 Starting Training on {DEVICE}...")

    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        
        for batch_i, (batch_X, batch_y) in enumerate(loader):
            batch_X, batch_y = batch_X.to(DEVICE), batch_y.to(DEVICE)
            
            optimizer.zero_grad()
            output = model(batch_X)
            loss = criterion(output, batch_y)
            loss.backward()
            
            # Gradient Clipping (Prevents "Exploding Gradients")
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            
            optimizer.step()
            total_loss += loss.item()

            if batch_i % 100 == 0:
                print(f"   Epoch {epoch+1} | Batch {batch_i}/{len(loader)} | Loss: {loss.item():.6f}", end="\r")

        avg_loss = total_loss / len(loader)
        scheduler.step(avg_loss)
        
        print(f"\n✅ Epoch {epoch+1}/{EPOCHS} | Avg Loss: {avg_loss:.6f} | LR: {optimizer.param_groups[0]['lr']:.6f}")

        # --- COOL DOWN STEP ---
        print("❄️ Cooling down GPU for 3 seconds...") 
        time.sleep(3)  # <--- The bot takes a breath here
        
        # --- SAVE BEST MODEL ---
        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f"💾 New Best Model Saved! (Loss: {best_loss:.6f})")
            patience_counter = 0
        else:
            patience_counter += 1
            print(f"⚠️ No improvement for {patience_counter} epochs.")
            
        # Early Stopping
        if patience_counter >= 7:
            print("🛑 Early Stopping triggered. Training complete.")
            break

    print("🎉 Training Finished. Use test_live_transformer.py to run it.")

if __name__ == "__main__":
    train()