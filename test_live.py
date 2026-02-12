import pickle
import torch
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import dukascopy_python
from dukascopy_python.instruments import INSTRUMENT_CFD_GOLD_XAU_USD

# ——— PARAMETERS ———
INSTRUMENT = INSTRUMENT_CFD_GOLD_XAU_USD
MINUTES_LOOKBACK = 180  # last 3 hours
WINDOW_SIZE = 60        # model input
FUTURE_STEPS = 3        # next 3 minutes

# ——— LOAD SCALER & MODEL ———
with open("scaler_xauusd.pkl", "rb") as f:
    scaler = pickle.load(f)

model = torch.load("lstm_xauusd.pt")
model.eval()

# ——— FETCH LIVE 1‑MIN CANDLES ———
end_time = datetime.utcnow()
start_time = end_time - timedelta(minutes=MINUTES_LOOKBACK)

df_gen = dukascopy_python.live_fetch(
    INSTRUMENT,
    1,
    dukascopy_python.TIME_UNIT_MIN,      # minute time‑unit
    dukascopy_python.OFFER_SIDE_BID,      # bid side (typical for OHLC)
    start_time,
    end_time
)

candles = None
for candles in df_gen:
    pass  # get the last frame of live data

if candles is None or len(candles) < MINUTES_LOOKBACK:
    raise RuntimeError("Not enough live data received")

candles = candles[-MINUTES_LOOKBACK:][["open","high","low","close"]]
candles.reset_index(drop=True, inplace=True)
print(f"Fetched {len(candles)} live 1‑minute candles up to {end_time} UTC")

# ——— SCALE DATA ———
scaled = scaler.transform(candles.values)

# ——— PREDICT FUTURE MINUTES ———
predicted_candles = []
data_seq = scaled.copy()

for step in range(FUTURE_STEPS):
    window = data_seq[-WINDOW_SIZE:]
    X = torch.FloatTensor(window).reshape(1, WINDOW_SIZE, 4)

    with torch.no_grad():
        out = model(X).numpy().reshape(-1)

    inv = scaler.inverse_transform(out.reshape(1, -1))[0]
    pred_open, pred_high, pred_low, pred_close = inv

    signal = "BUY" if pred_close > pred_open else "SELL"

    predicted_candles.append({
        "minute": step + 1,
        "open": pred_open,
        "high": pred_high,
        "low": pred_low,
        "close": pred_close,
        "signal": signal
    })

    scaled_next = scaler.transform(np.array([inv]))
    data_seq = np.vstack([data_seq, scaled_next])

print("\n=== Live 3‑Minute Predictions with Signals ===")
for p in predicted_candles:
    print(f"Minute +{p['minute']}:")
    print(f"  Open:  {p['open']:.2f}")
    print(f"  High:  {p['high']:.2f}")
    print(f"  Low:   {p['low']:.2f}")
    print(f"  Close: {p['close']:.2f}")
    print(f"  Signal: {p['signal']}")

print("\nDone.")
