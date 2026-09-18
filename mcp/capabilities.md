# AI Capabilities in this Environment

## What you have
- DuckDB (SQL) with many extensions ; see runtime/manifest.md for exact list
- Python 3.12 with a broad data/ML stack ; see runtime/manifest.md for versions
- Our custom toolkit (helpers we built)

## Our toolkit (use these when applicable)
- toolkit.parallel.ParallelRunner ; run many queries in parallel
- toolkit.jobs.JobScheduler ; schedule cron/interval jobs inside Jupyter
- toolkit.lakehouse.{iceberg_attach, ducklake_attach, delta_scan, lance_scan, lance_write}
- toolkit.ml.{init_mlflow, track_run, log_regression_metrics, split, torch_device}
- toolkit.io_helpers.{to_parquet, to_csv, to_qvd, read_any}
- toolkit.rag.{create_index, search, build_prompt} ; RAG with embeddings
- toolkit.transcribe.{transcribe_to_text, transcribe_to_srt} ; Whisper STT
- toolkit.maintenance.{install_python_package, install_duckdb_extension, change_ai_model}
## Project conventions
- Prefer DuckDB SQL for analytics
- Write outputs to: exports/, reports/, data/, logs/, mlruns/
- Use Parquet for intermediate files
- Style: PEP 8, type hints where helpful
- Ask before running DROP / TRUNCATE / DELETE without WHERE

## Environment
- Offline after setup (no internet)
- No GPU (CPU-only models)
- Read MCP resources: business context, manifest, capabilities

## You already know standard libraries
You know pandas, numpy, matplotlib, plotly, streamlit, sklearn, torch
from training. Don't re-read their docs; just use them. Focus your
attention on OUR toolkit and the business context above.