import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import joblib

# ===========================
# CONFIG
# ===========================
SEQ_LEN = 64
BATCH_SIZE = 64
EPOCHS = 5
LR = 0.001
DATA_FILE = "Gold_Data_XAUUSD/train.parquet"  # adjust your training file path
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ===========================
# MODEL
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
# TRAIN FUNCTION
# ===========================
def train(model, X, y, epochs=EPOCHS):
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    criterion = nn.MSELoss()
    dataset = torch.utils.data.TensorDataset(torch.tensor(X, dtype=torch.float32),
                                             torch.tensor(y, dtype=torch.float32))
    loader = torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    for epoch in range(epochs):
        total_loss = 0
        for xb, yb in loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            optimizer.zero_grad()
            pred = model(xb)
            loss = criterion(pred, yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * xb.size(0)
        print(f"Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(X):.6f}")
    return model

# ===========================
# DATA PREPARATION
# ===========================
def create_sequences(data, seq_len=SEQ_LEN):
    X, y = [], []
    for i in range(len(data)-seq_len):
        X.append(data[i:i+seq_len])
        y.append(data[i+seq_len][:4])  # predict OHLC
    return np.array(X), np.array(y)

# ===========================
# MAIN
# ===========================
if __name__ == "__main__":
    print(f"Training on {DEVICE}")
    df = pd.read_parquet(DATA_FILE)
    df = df.sort_values("timestamp").reset_index(drop=True)
    scaler = joblib.load("scaler_xauusd.pkl") if False else None  # replace with actual scaler if exists

    data = df[['open','high','low','close','volume']].values
    if scaler is None:
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        scaler.fit(data)
    joblib.dump(scaler, "scaler_xauusd.pkl")

    data_scaled = scaler.transform(data)
    X, y = create_sequences(data_scaled)
    model = LSTMModel().to(DEVICE)

    trained_model = train(model, X, y, EPOCHS)
    torch.save(trained_model.state_dict(), "lstm_xauusd.pt")
    print("Training finished. Model and scaler saved.")
