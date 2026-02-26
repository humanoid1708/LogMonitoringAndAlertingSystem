# models/anomaly_lstm.py
import torch
import torch.nn as nn

class LSTMAutoEncoder(nn.Module):
    def __init__(self, n_features, hidden=32):
        super().__init__()
        self.encoder = nn.LSTM(n_features, hidden, batch_first=True)
        self.decoder = nn.LSTM(hidden, n_features, batch_first=True)

    def forward(self, x):
        _, (h, _) = self.encoder(x)
        h = h.repeat(x.size(1), 1, 1).permute(1,0,2)
        out, _ = self.decoder(h)
        return out