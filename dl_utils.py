# dl_utils.py
import torch
import numpy as np

def build_sequences(df, window=5):
    """
    Convert feature dataframe into time-series sequences for LSTM
    """
    data = df[["error_count", "log_count", "avg_response_time"]].values
    sequences = []

    for i in range(len(data) - window):
        sequences.append(data[i:i + window])

    return torch.tensor(np.array(sequences), dtype=torch.float32)