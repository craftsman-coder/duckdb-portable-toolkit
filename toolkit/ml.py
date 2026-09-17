"""ML helpers: MLflow tracking + PyTorch utilities."""

from __future__ import annotations

from contextlib import contextmanager

import mlflow
import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, f1_score, mean_absolute_error,
                             mean_squared_error, r2_score)
from sklearn.model_selection import train_test_split

from toolkit.config import MLRUNS_DIR

def init_mlflow(experiment="default"):
    tracking = MLRUNS_DIR.resolve()
    tracking.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(f"file://{tracking}")
    mlflow.set_experiment(experiment)
    return mlflow.get_tracking_uri()

@contextmanager
def track_run(run_name, params=None, tags=None):
    with mlflow.start_run(run_name=run_name) as run:
        if params:
            mlflow.log_params(params)
        if tags:
            mlflow.set_tags(tags)
        yield run

def log_regression_metrics(y_true, y_pred, prefix=""):
    m = {
        f"{prefix}mae": mean_absolute_error(y_true, y_pred),
        f"{prefix}rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        f"{prefix}r2": r2_score(y_true, y_pred),
    }
    mlflow.log_metrics(m)
    return m

def log_classification_metrics(y_true, y_pred, prefix=""):
    m = {
        f"{prefix}accuracy": accuracy_score(y_true, y_pred),
        f"{prefix}f1": f1_score(y_true, y_pred, average="weighted"),
    }
    mlflow.log_metrics(m)
    return m

def split(df, target, test_size=0.2, random_state=42):
    X = df.drop(columns=[target])
    y = df[target]
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

def torch_device():
    import torch
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")

def torch_dataloader(X, y, batch_size=64, shuffle=True):
    import torch
    from torch.utils.data import DataLoader, TensorDataset
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32).reshape(-1, 1)
    return DataLoader(TensorDataset(X_t, y_t), batch_size=batch_size, shuffle=shuffle)

def log_torch_model(model, name="model"):
    mlflow.pytorch.log_model(model, name)