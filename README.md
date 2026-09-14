# Portable DuckDB Toolkit

A fully portable data + ML environment that runs inside Jupyter and Streamlit.
Works on Windows and Linux. After the initial setup, everything runs offline.

## How it works

- All install choices live in config.yaml.
- setup.py reads config.yaml and installs everything into folders inside
  the project (fully portable).
- After setup, nothing needs internet.
- verify.py checks that everything is correctly installed.

## Quick start

### 1. Clone

    git clone https://github.com/YOUR-USERNAME/duckdb-portable-toolkit.git
    cd duckdb-portable-toolkit

### 2. Edit config.yaml

Common changes:

    paths:
      project_root: "D:/duckdb-toolkit"

    pytorch:
      build: "cuda"
      cuda_version: "cu121"

    runtime:
      duckdb_memory_limit: "200GB"
      duckdb_threads: 16

### 3. Run setup (needs internet once)

    python setup.py

### 4. Verify

    python verify.py

### 5. Launch Jupyter

    # Windows
    python_portable\Scripts\jupyter-lab.exe

    # Linux
    python_portable/bin/jupyter-lab

### 6. Launch a Streamlit dashboard

    # Windows
    python_portable\Scripts\streamlit.exe run dashboards\01_orders_dashboard.py

    # Linux
    python_portable/bin/streamlit run dashboards/01_orders_dashboard.py

Open http://localhost:8501.

## Examples

- 01_basic_queries.py          - Run SQL against DuckDB
- 02_parallel_queries.py       - Run many queries at once
- 03_scheduled_jobs.py         - Schedule a daily job
- 07_machine_learning.py       - scikit-learn + MLflow
- 09_lakehouse_formats.py      - Iceberg, Delta, Lance, DuckLake

## Dashboards

- 01_orders_dashboard.py       - KPIs, table, charts
- 03_sql_workbench.py          - Run arbitrary SQL

## Scheduling jobs

    from toolkit.jobs import JobScheduler
    scheduler = JobScheduler()
    scheduler.add_cron_job("daily_export", "jobs/example_daily_export.py",
                           hour=0, minute=30)
    scheduler.start()

## Database connections

Edit configs/secrets.sql with your credentials:

    import duckdb
    con = duckdb.connect()
    con.execute(open("configs/secrets.sql").read())
    df = con.execute(
        "SELECT * FROM oracle_query('ora', 'SELECT * FROM sales') LIMIT 10"
    ).fetchdf()

## Uninstall

Delete the project folder. Nothing was installed on the system.

## License

MIT - see the LICENSE file.
