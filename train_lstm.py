import torch
import pandas as pd
from torch import nn, optim
from torch.utils.data import DataLoader, TensorDataset

# ==============================
# 1️⃣ تأكد من الجهاز (GPU/CPU)
# ==============================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("======================================")
if device.type == "cuda":
    print(f"Training on GPU: {torch.cuda.get_device_name(0)}")
else:
    print("GPU not available, training on CPU")
print("======================================\n")

# ==============================
# 2️⃣ تحميل البيانات
# ==============================
file_path = "Gold_Data_XAUUSD/train1.parquet"
df = pd.read_parquet(file_path)

# استخدام الأعمدة الصحيحة من Dukascopy
data = df[['open', 'high', 'low', 'close', 'volume']].values
data = torch.tensor(data, dtype=torch.float32)

# ==============================
# 3️⃣ إعداد sequences للتدريب
# ==============================
SEQ_LEN = 60  # نافذة زمنية: 60 دقيقة
X, y = [], []
for i in range(len(data) - SEQ_LEN):
    X.append(data[i:i+SEQ_LEN])
    y.append(data[i+SEQ_LEN, 3])  # التنبؤ بسعر الإغلاق للشمعة التالية (close)

X = torch.stack(X).to(device)
y = torch.tensor(y, dtype=torch.float32).to(device)

dataset = TensorDataset(X, y)
loader = DataLoader(dataset, batch_size=128, shuffle=True)

# ==============================
# 4️⃣ بناء LSTM
# ==============================
class LSTMModel(nn.Module):
    def __init__(self, input_size=5, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]  # آخر خطوة في sequence
        out = self.fc(out)
        return out.squeeze()

model = LSTMModel().to(device)
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()

# ==============================
# 5️⃣ التدريب
# ==============================
EPOCHS = 5  # يمكنك زيادة العدد لاحقًا
for epoch in range(EPOCHS):
    total_loss = 0
    for xb, yb in loader:
        optimizer.zero_grad()
        preds = model(xb)
        loss = criterion(preds, yb)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {total_loss/len(loader):.6f}")

# ==============================
# 6️⃣ حفظ الموديل والتدريب
# ==============================
torch.save({
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'SEQ_LEN': SEQ_LEN
}, "lstm_xauusd.pt")

print("\n✅ Training finished. Model saved as lstm_xauusd.pt")
