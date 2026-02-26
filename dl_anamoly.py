# dl_anomaly.py
import torch

def compute_dl_anomaly(model, sequences):
    model.eval()
    with torch.no_grad():
        recon = model(sequences)
        loss = torch.mean((sequences - recon) ** 2, dim=(1,2))
    return loss.numpy()