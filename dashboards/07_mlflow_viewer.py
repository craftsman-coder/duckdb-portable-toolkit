"""Browse local MLflow runs."""

import os
from pathlib import Path

# Allow the filesystem tracking backend (needed for MLflow 3.x)
os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")

import pandas as pd
import streamlit as st

from _common import page_header

page_header("MLflow runs", "Browse runs stored in ./mlruns.")

# Resolve mlruns directory relative to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
tracking = (PROJECT_ROOT / "mlruns").resolve()

if not tracking.exists():
    st.warning(f"No MLflow tracking dir at {tracking}.")
    st.info(
        "Run a training example first, for example:\n"
        "  examples/07_machine_learning.py\n"
        "  examples/08_mlflow_tracking.py"
    )
    st.stop()


def _mlflow_uri(path: Path) -> str:
    """Build a cross-platform MLflow file:// URI."""
    p = path.as_posix()                # C:/projects/... (forward slashes)
    if not p.startswith("/"):
        p = "/" + p                    # /C:/projects/...
    return "file://" + p               # file:///C:/projects/...


uri = _mlflow_uri(tracking)
st.caption(f"Tracking URI: {uri}")

import mlflow
mlflow.set_tracking_uri(uri)

try:
    runs = mlflow.search_runs()
except Exception as exc:
    st.error(f"Could not read MLflow runs: {exc}")
    st.info(
        "If you have no runs yet, run a training example first:\n"
        "  examples/07_machine_learning.py"
    )
    st.stop()

if runs.empty:
    st.info("No runs yet.")
    st.stop()

st.metric("Total runs", len(runs))

display = ["run_id", "experiment_id", "status", "start_time"]
display += [c for c in runs.columns if c.startswith("metrics.")]
display += [c for c in runs.columns if c.startswith("params.")]
display = [c for c in display if c in runs.columns]
st.dataframe(runs[display], use_container_width=True)

metric_cols = [c for c in runs.columns if c.startswith("metrics.")]
if metric_cols:
    st.subheader("Metrics across runs")
    metric = st.selectbox("Metric", metric_cols)
    chart = runs[["start_time", metric]].dropna().sort_values("start_time")
    st.line_chart(chart, x="start_time", y=metric)

st.subheader("Run details")
run_id = st.selectbox("Run", runs["run_id"].tolist())
if run_id:
    row = runs[runs["run_id"] == run_id].iloc[0]
    st.json({k: str(v) for k, v in row.items() if pd.notna(v)})