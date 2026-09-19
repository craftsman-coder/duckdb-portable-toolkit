# AI Capabilities in this Environment

## What you have
- DuckDB (SQL) with many extensions; see runtime/manifest.md for exact list
- Python 3.12 with a broad data/ML stack; see runtime/manifest.md for versions
- Our custom toolkit (helpers we built)

## Our toolkit (use these when applicable)
- toolkit.parallel.ParallelRunner; run many queries in parallel
- toolkit.jobs.JobScheduler; schedule cron/interval jobs inside Jupyter
- toolkit.lakehouse.{iceberg_attach, ducklake_attach, delta_scan, lance_scan, lance_write}
- toolkit.ml.{init_mlflow, track_run, log_regression_metrics, split, torch_device}
- toolkit.io_helpers.{to_parquet, to_csv, to_qvd, read_any}
- toolkit.rag.{create_index, search, build_prompt}; RAG with embeddings
- toolkit.transcribe.{transcribe_to_text, transcribe_to_srt}; Whisper STT
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

## Connectors (remote servers)
Use `toolkit.connections` to talk to remote Kafka, Flink, and
Trino clusters from Python. No Docker, no local cluster needed.

### Kafka
- `connections.kafka_consumer(bootstrap, topics=[...])`; consume
- `connections.kafka_producer(bootstrap)`; produce
- `connections.kafka_topics(bootstrap)`; list topics
- `connections.kafka_consume_once(bootstrap, topic, max_messages=100)`
- `connections.read_kafka_topic_via_duckdb(con, broker, topic)`

### Flink SQL
- `connections.flink_sql_connect(gateway_url)`; DBAPI connection
- `connections.flink_sql_query(gateway_url, sql)`; run SQL
- `connections.flink_jobs(jobmanager_url)`; list jobs
- `connections.flink_job_status(job_id, jobmanager_url)`
- `connections.flink_cluster_info(jobmanager_url)`

### Trino
- `connections.trino_connect(host, port, user, catalog, schema)`
- `connections.trino_query(host, sql)`; returns a pandas DataFrame
- `connections.trino_catalogs(host)`

### Generic
- `connections.sqlalchemy_engine(uri)`; any database

## Online AI (optional)
If `online_ai.enabled` is true in config.yaml, you can call
a remote model through OpenRouter, OpenAI, or any other
OpenAI-compatible provider.

- `online_ai.chat(prompt, system=..., model=...)`; single reply
- `online_ai.chat_stream(...)`; streaming reply
- `online_ai.litellm_chat(prompt, model='openrouter/...')`; 100+ providers
- `online_ai.list_providers()`; built-in presets

Use it when the local model is not enough (bigger context,
better reasoning, another language, etc.).
