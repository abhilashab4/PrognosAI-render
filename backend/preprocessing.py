from io import BytesIO
import os
import pandas as pd
import numpy as np
import joblib

from backend.s3_service import download_file


def create_test_sequences(df, sequence_length=50):
    X = []
    engine_ids = df["engine_id"].unique()

    for eid in engine_ids:
        engine_df = df[df["engine_id"] == eid].sort_values("cycle")
        engine_features = engine_df.drop(columns=["engine_id", "cycle"]).values
        n_cycles = engine_features.shape[0]

        if n_cycles >= sequence_length:
            X.append(engine_features[-sequence_length:])
        else:
            pad = np.zeros((sequence_length - n_cycles, engine_features.shape[1]))
            X.append(np.vstack([pad, engine_features]))

    return np.array(X, dtype=np.float32)


def preprocess_test_file(file, scaler):
    df = pd.read_csv(BytesIO(file), sep=" ", header=None)
    df = df.iloc[:, :26]

    col_names = [
        "engine_id", "cycle",
        "op1", "op2", "op3",
        "s1", "s2", "s3", "s4", "s5",
        "s6", "s7", "s8", "s9", "s10",
        "s11", "s12", "s13", "s14", "s15",
        "s16", "s17", "s18", "s19", "s20", "s21"
    ]
    df.columns = col_names

    sensor_cols = col_names[2:]
    df[sensor_cols] = scaler.transform(df[sensor_cols])

    dead_sensors = [c for c in sensor_cols if df[c].nunique() == 1]
    df = df.drop(columns=dead_sensors)

    return df


def load_scaler(domain: str):
    local_path = f"notebook/{domain}_scaler.joblib"
    s3_key = f"scalers/{domain}_scaler.joblib"

    if not os.path.exists(local_path):
        download_file(s3_key, local_path)

    return joblib.load(local_path)