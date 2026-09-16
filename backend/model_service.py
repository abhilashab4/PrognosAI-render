import os
import numpy as np
import torch

from notebook.architecture import GRUModel
from backend.s3_service import download_file


def load_model(domain: str, X_seq: np.ndarray):
    input_size = X_seq.shape[2]
    local_path = f"models/{domain}_model.pth"
    s3_key = f"models/{domain}_model.pth"

    if not os.path.exists(local_path):
        download_file(s3_key, local_path)

    model = GRUModel(input_size=input_size)
    model.load_state_dict(torch.load(local_path, map_location="cpu"))
    model.eval()

    return model


def predict_rul(X_seq, model):
    model.eval()
    with torch.no_grad():
        X_tensor = torch.tensor(X_seq, dtype=torch.float32)
        predictions = model(X_tensor).numpy().flatten()

    return predictions