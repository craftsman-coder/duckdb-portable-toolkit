"""Browse local MLflow runs."""

from pathlib import Path

import pandas as pd
import streamlit as st

from _common import page_header

page_header("MLflow runs", "Browse runs stored in ./mlruns.")

tracking = Path("mlruns").resolve()
if not tracking.exists():
    st.warning(f"No MLflow tracking dir at {tracking}.")
    st.stop()

import mlflow
mlflow.set_tracking_uri(f"file://{tracking}")

try:
    runs = mlflow.search_runs()
except Exception as exc:
    st.error(str(exc))
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