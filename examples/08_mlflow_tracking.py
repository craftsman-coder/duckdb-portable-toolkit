# %% [markdown]
# # 08 - PyTorch + MLflow

# %%
import numpy as np
import torch
import torch.nn as nn

from toolkit.ml import (init_mlflow, track_run, torch_device,
                        torch_dataloader, log_torch_model)

# %%
init_mlflow(experiment="demo-torch")

# %%
rng = np.random.default_rng(0)
X = rng.normal(size=(4000, 5)).astype("float32")
w_true = np.array([2.0, -1.0, 0.5, 0.0, 3.0], dtype="float32")
y = (X @ w_true + rng.normal(scale=0.1, size=4000)).astype("float32")
loader = torch_dataloader(X, y, batch_size=64)

# %%
device = torch_device()
print("device:", device)
model = nn.Sequential(nn.Linear(5, 32), nn.ReLU(), nn.Linear(32, 1)).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
loss_fn = nn.MSELoss()

# %%
with track_run("torch-linear", params={"epochs": 5, "lr": 1e-2}):
    for epoch in range(5):
        total = 0.0
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            optimizer.step()
            total += loss.item() * len(xb)
        print(f"epoch {epoch + 1}: loss={total / len(loader.dataset):.4f}")
    log_torch_model(model, name="torch_regressor")
