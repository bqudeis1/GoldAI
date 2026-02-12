import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import joblib

# ===========================
# CONFIG
# ===========================
SEQ_LEN = 64
TEST_FOLDER = "Gold_Data_XAUUSD"
MODEL_PATH = "lstm_xauusd.pt"
SCALER_PATH = "scaler_xauusd.pkl"
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
# HELPERS
# ===========================
scaler = joblib.load(SCALER_PATH)
model = LSTMModel().to(DEVICE)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()

def inverse_normalize(pred):
    dummy = np.zeros((1, 5))
    dummy[0,:4] = pred
    inv = scaler.inverse_transform(dummy)
    return inv[0,:4]

def buy_sell_signal(pred_seq, prev_close, threshold=0.001):
    avg_future = np.mean(pred_seq)
    change = (avg_future - prev_close) / prev_close
    if change > threshold:
        return 1  # Buy
    elif change < -threshold:
        return 0  # Sell
    else:
        return None

# ===========================
# TEST LOOP
# ===========================
test_files = [f"{TEST_FOLDER}/test1.parquet"]

for file in test_files:
    df = pd.read_parquet(file)
    df = df.sort_values("timestamp").reset_index(drop=True)
    data = df[['open','high','low','close','volume']].values

    day_accs = []

    for start_idx in range(0, len(data), 1440):
        day_data = data[start_idx:start_idx+1440]
        if len(day_data) < SEQ_LEN + 3:
            continue

        ohlc_acc_list = []
        buy_sell_acc_list = []

        for i in range(len(day_data) - SEQ_LEN - 2):
            seq_x = day_data[i:i+SEQ_LEN]
            seq_x_norm = scaler.transform(seq_x)
            seq_tensor = torch.tensor(seq_x_norm, dtype=torch.float32).unsqueeze(0).to(DEVICE)

            with torch.no_grad():
                # predict next 3 steps
                preds = []
                for j in range(3):
                    window = day_data[i+j:i+SEQ_LEN+j]
                    window_norm = scaler.transform(window)
                    pred_norm = model(torch.tensor(window_norm, dtype=torch.float32).unsqueeze(0).to(DEVICE))
                    preds.append(inverse_normalize(pred_norm.detach().cpu().numpy()[0]))

            true = day_data[i+SEQ_LEN][:4]
            ohlc_pred = preds[0]

            # OHLC accuracy
            ohlc_acc = 1 - np.mean(np.abs(ohlc_pred - true)/true)
            ohlc_acc_list.append(ohlc_acc)

            # Buy/Sell accuracy
            signal = buy_sell_signal([p[3] for p in preds], seq_x[-1,3])
            true_signal = 1 if true[3] > seq_x[-1,3] else 0
            if signal is not None:
                buy_sell_acc_list.append(1 if signal == true_signal else 0)

        avg_ohlc_acc = np.mean(ohlc_acc_list)
        avg_buy_sell_acc = np.mean(buy_sell_acc_list) if buy_sell_acc_list else 0
        day_accs.append((avg_ohlc_acc, avg_buy_sell_acc))
        print(f"Day {file.split('/')[-1]} - OHLC Accuracy: {avg_ohlc_acc:.4f}, Buy/Sell Accuracy: {avg_buy_sell_acc:.4f}")

    daily_ohlc = [d[0] for d in day_accs]
    daily_bs = [d[1] for d in day_accs]
    print(f"Final OHLC Accuracy: {np.mean(daily_ohlc):.4f}, Final Buy/Sell Accuracy: {np.mean(daily_bs):.4f}")
