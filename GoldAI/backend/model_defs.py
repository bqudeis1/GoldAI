import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:x.size(0), :]

class TradingTransformer(nn.Module):
    def __init__(self, input_dim=5, d_model=64, nhead=4, num_layers=2, output_dim=4, dropout=0.1):
        super(TradingTransformer, self).__init__()
        
        # 1. Feature Embedding (Turn 5 inputs into 64 features)
        self.embedding = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        
        # 2. The Transformer Encoder (The Brain)
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=128, dropout=dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        
        # 3. Output Head (Prediction)
        self.decoder = nn.Linear(d_model, output_dim)

    def forward(self, src):
        # src shape: [batch_size, seq_len, features]
        # Transformer expects: [seq_len, batch_size, features]
        src = src.permute(1, 0, 2)
        
        src = self.embedding(src)
        src = self.pos_encoder(src)
        output = self.transformer_encoder(src)
        
        # We only care about the LAST time step (the prediction)
        # Shape: [1, batch_size, output_dim] -> [batch_size, output_dim]
        output = self.decoder(output[-1, :, :])
        return output