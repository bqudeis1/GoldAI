# GoldAI - XAU/USD Price Predictor

GoldAI predicts minute-level XAU/USD (Gold) prices using an LSTM model trained on historical data from Dukascopy.

---

## Features

- Predicts minute-level Open, High, Low, Close (OHLC)  
- Predicts Buy/Sell signals  
- Calculates daily and overall accuracy  
- Uses GPU for faster training (CUDA supported)  
- Handles Parquet files for fast reading/writing  
- Saves trained model and scaler for later use or incremental training  

---

## Requirements

- Windows or Linux  
- Python 3.10 (recommended for compatibility)  
- NVIDIA GPU with CUDA support (tested with RTX 4060, CUDA 12.8/13)  

---

## Step-by-Step Installation & Setup

### 1. Install Python 3.10

Check if Python 3.10 is installed:
```powershell
py -3.10 --version

If not, download and install from: https://www.python.org/downloads/release/python-31011/

Install Git (if not installed)

Check Git version:

git --version


Download Git if needed: https://git-scm.com/downloads

## Clone this repository

git clone https://github.com/bqudeis1/GoldAI.git
cd GoldAI


### (Optional) Create a virtual environment

py -3.10 -m venv venv
.\venv\Scripts\activate


### Upgrade pip

python -m pip install --upgrade pip


### Install required Python packages

pip install pandas pyarrow scikit-learn matplotlib


### Install PyTorch with GPU support

For CUDA 12.8:

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128


### Check installation and GPU availability:

import torch
print("GPU available:", torch.cuda.is_available())
print("GPU name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None")

### Preparing Data

Place your Parquet files in Gold_Data_XAUUSD folder:

Gold_Data_XAUUSD/
    train1.parquet  # 5-year training data
    test1.parquet   # test data (~12 days)
    test2.parquet   # optional additional test files

### Running the Project
Training the Model
py -3.10 .\train_lstm.py


Trains the LSTM on train1.parquet

Uses GPU if available

Saves:

Model: lstm_xauusd.pt

Scaler: scaler_xauusd.pkl

Shows training loss per epoch

### Testing / Prediction
py -3.10 .\test_lstm.py


### Loads trained model and scaler

Uses first 60 minutes to predict the next minute, then slides the window until the end of each day

Predicts OHLC and Buy/Sell for each file in Gold_Data_XAUUSD

Calculates daily and overall accuracy

### Output:

Daily OHLC accuracy

Daily Buy/Sell accuracy

Final average accuracy across all test days

### Folder Structure
GoldAI/
│
├─ train_lstm.py           # Training script
├─ test_lstm.py            # Testing / prediction script
├─ lstm_xauusd.pt          # Saved trained model
├─ scaler_xauusd.pkl       # Saved scaler
├─ Gold_Data_XAUUSD/       # Parquet data folder
│   ├─ train1.parquet      # 5-year training data
│   ├─ test1.parquet       # Test data
│   └─ test2.parquet       # Optional additional test files

### Notes

Always run scripts using Python 3.10: py -3.10 script.py

Keep model and scaler in the same folder as scripts

You can add multiple test Parquet files; the script loops through all of them automatically

To continue training with new data, run train_lstm.py again; rename saved model if you want to keep old one

### License

© Baha Qudeisat

