import torch
import numpy as np

def anomaly_score(model, data):
    model.eval()
    with torch.no_grad():
        recon = model(data)
        loss = ((data - recon) ** 2).mean(dim=(1,2))
    return loss.numpy()