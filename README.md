# DuckDB Toolkit

**DuckDB Toolkit** is a portable, offline-ready environment for working
with data at high speed. It brings together DuckDB, JupyterLab,
Streamlit, a local language model, and BI drivers inside one folder;
no installation, no admin rights, no virtual environment.

It is built for the people who work with data every day:

- **Data engineers** building pipelines and lakehouse workloads
- **BI developers** prototyping metrics and reports
- **Context engineers** who design the business context, data
  dictionaries, and prompts that make a local AI useful for the
  organization; they can also prepare geospatial, financial,
  industrial, or any other kind of data for that purpose
- **Data scientists** exploring datasets and training models
- **Analysts** who want fast SQL, notebooks, and a local AI assistant

With the included toolset you can:

- Pull data from databases and files across many formats: Parquet, CSV, JSON, Excel, QVD, and remote databases (PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, Cassandra, and more)
- **Join and process them at high speed** in a single DuckDB query
- **Transcribe audio files to text** locally with Whisper
- **Teach a local AI** about your organization and ask it questions in plain language
- **Design data pipelines** and schedule them
- **See the results** as interactive tables and charts

Run it on a laptop or a development server, online or offline, on
**Windows, Linux, or macOS**. Just clone and start working.

---

## What you can do

1. **Pull data from anywhere**
   Read Parquet, CSV, JSON, Excel, QVD, and remote databases
   (PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, Cassandra)
   through DuckDB extensions.

2. **Join, filter, and compute**
   Run full SQL in DuckDB with window functions, CTEs, and spatial
   operations. Combine data from MinIO/S3, Parquet files, and
   databases in one query.

3. **Teach a local AI your business**
   The MCP server exposes your tables, schema, and business context
   to a local LLM (Qwen via llama.cpp). Ask it in plain language.

4. **Design data pipelines**
   Schedule jobs with `toolkit.jobs`, run queries in parallel with
   `toolkit.parallel`, and export to Parquet / QVD.

5. **Visualize results**
   Build interactive Streamlit dashboards, or chart directly in
   Jupyter with matplotlib, seaborn, plotly, altair, bokeh, and
   holoviews.

6. **Connect BI tools**
   ODBC and JDBC drivers ship with the toolkit; plug Tableau,
   Power BI, or Qlik Sense straight into your DuckDB files.

---

## Quick start

### 1. Clone

```bash
git clone https://github.com/YOUR-USERNAME/duckdb-toolkit.git
cd duckdb-toolkit
```

### 2. Run setup (needs internet once)

```bash
python setup.py
```

Choose a profile when asked:

| Option | Profile | Description | Size |
|---|---|---|---|
| 1 | light | DuckDB + Jupyter | ~700 MB |
| 2 | standard | + viz + ML + AI + MCP | ~2.5 GB |
| 3 | full | + EDA + MLflow + all extensions | ~5.7 GB |
| 4 | custom | Like full, but you edit config first | varies |

You can skip the prompt:

```bash
python setup.py --profile standard
```

### 3. Verify

```bash
python verify.py
```

### 4. Launch JupyterLab

```bash
# Windows
runtime\venv\Scripts\jupyter-lab.exe

# Linux
runtime/venv/bin/jupyter-lab
```

Open `http://localhost:8888` in your browser.

### 5. Launch a Streamlit dashboard

Streamlit runs in a browser tab at `http://localhost:8501`.

```bash
# Windows
runtime\venv\Scripts\streamlit.exe run dashboards\01_orders_dashboard.py

# Linux
runtime/venv/bin/streamlit run dashboards/01_orders_dashboard.py
```

Inside JupyterLab:

```python
from toolkit.ui import start_streamlit
start_streamlit("dashboards/01_orders_dashboard.py")
```

---

## Who is this for?

| Role | What you get |
|---|---|
| **Data engineers** | DuckDB for lakehouse workloads, Iceberg / Delta / Lance support, job scheduler, parallel query runner, and a growing set of database connectors (PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, Cassandra) |
| **BI developers** | 50+ Python packages, Streamlit dashboards, ODBC / JDBC drivers to plug into Tableau / Power BI / Qlik, one-click dashboards |
| **Dashboard developers** | Streamlit + DuckDB for fast, refreshing dashboards on top of Parquet or live databases |
| **Context engineers** | Geospatial (GeoPandas + DuckDB spatial), time series, Excel / CSV, QVD for Qlik |
| **Data scientists** | pandas / polars / PyArrow, scikit-learn, XGBoost, LightGBM, PyTorch, MLflow, Optuna, ydata-profiling |
| **Analysts** | JupyterLab for notebook analysis, DuckDB UI for direct SQL, local AI for Q&A on your data |

---

## All-in-one launchers

After cloning, **every task** can be done with a double-click
(Windows) or a single command (Linux / macOS / Git Bash).

| Task | Windows | Linux / macOS / Git Bash |
|---|---|---|
| **Install** the toolkit | `setup.bat` | `./setup.sh` |
| **Verify** the installation | `verify.bat` | `./verify.sh` |
| Launch **JupyterLab** | `start-jupyter.bat` | `./start-jupyter.sh` |
| Launch **Streamlit** dashboards | `start-streamlit.bat` | `./start-streamlit.sh` |
| Launch **DuckDB UI** | `start-duck-ui.bat` | `./start-duck-ui.sh` |

### First-time setup (in order)

1. **Install**; double-click `setup.bat` (or run `./setup.sh`).
   Choose a profile when prompted:
   `1` light, `2` standard (recommended), `3` full, `4` custom.
2. **Verify**; double-click `verify.bat` (or run `./verify.sh`).
   All checks should show `[ok]`.
3. **Start working**; double-click `start-jupyter.bat` (or `./start-jupyter.sh`).
   The browser opens automatically at http://localhost:8888.

On Linux / macOS, make the scripts executable once:

```bash
chmod +x setup.sh verify.sh start-*.sh
```

### DuckDB UI

`start-duck-ui.bat` (Windows) or `start-duck-ui.sh` (Linux / macOS)
launches the **DuckDB web UI** at http://localhost:4213.

- SQL editor with syntax highlighting
- Data explorer with tables and simple charts
- File import from Parquet / CSV
- Uses the `ui` extension, installed automatically by `setup`
- **First launch downloads ~10 MB of frontend assets**; after that,
  it works fully offline.

> **Note:** DuckDB UI needs internet **only on the first launch** to
> cache frontend assets. On an air-gapped server, launch it once
> while online, then use it offline.

---

## Launch JupyterLab

Three ways to start JupyterLab. Pick whichever is easiest for you.

### Option 1: Double-click (Windows)

Double-click `start-jupyter.bat` in the project folder.

That's it. The browser opens automatically at `http://localhost:8888/lab`.

### Option 2: Double-click (Linux / macOS)

Double-click `start-jupyter.sh`, or run it from a terminal:

```bash
./start-jupyter.sh
```

If it is the first time, make it executable:

```bash
chmod +x start-jupyter.sh
```

### Option 3: From a terminal (any OS)

Windows (PowerShell or CMD):

```powershell
cd C:\projects\duckdb-toolkit
runtime\venv\Scripts\jupyter-lab.exe
```

Linux / macOS / Git Bash:

```bash
cd /path/to/duckdb-toolkit
runtime/venv/bin/jupyter-lab
```

### After it starts

The terminal prints a URL like this:

    http://localhost:8888/lab?token=594bf1da49163f5649798767c6a9c2c6b73179c7e2059875

Open that URL in your browser (copy the whole thing, including the token).

### Stopping Jupyter

In the terminal where Jupyter is running, press Ctrl+C twice.

### Changing the port

If port 8888 is already used by another program:

```bash
# Windows
runtime\venv\Scripts\jupyter-lab.exe --port 8889

# Linux / macOS
runtime/venv/bin/jupyter-lab --port 8889
```

Then open `http://localhost:8889/lab`.

### Accessing from another machine (LAN)

To let colleagues open your Jupyter from their computers:

```bash
# Windows
runtime\venv\Scripts\jupyter-lab.exe --ip 0.0.0.0 --port 8888

# Linux / macOS
runtime/venv/bin/jupyter-lab --ip 0.0.0.0 --port 8888
```

Then they open `http://YOUR-IP:8888/lab`.

### Troubleshooting

**"Bad config: No such directory"**
- Use `start-jupyter.bat` (Windows) or `start-jupyter.sh` (Linux).
- They set the working directory automatically.

**"No module named 'toolkit'"**
- Make sure you launched Jupyter from the project root.
- The launcher scripts already do this.

**Browser does not open automatically**
- Copy the URL from the terminal and paste it into your browser manually.
- The token is required, so include everything after `?token=`.

**"Address already in use"**
- Use a different port: `--port 8889` (see above).

## Managing your toolkit

Everything you need is in `toolkit.maintenance`. Run these from any
Jupyter cell.

### Install a Python package

```python
from toolkit.maintenance import install_python_package
install_python_package("statsmodels")
```

### Install a DuckDB extension

```python
from toolkit.maintenance import install_duckdb_extension
install_duckdb_extension("httpfs")
install_duckdb_extension("qvd", community=True)
```

### Change the AI model

```python
from toolkit.maintenance import change_ai_model
change_ai_model("qwen2.5-7b")
```

Then pull the model:

```bash
```

See `docs/AI_MODELS.md` to switch to a bigger model or enable GPU.

### See what's installed

```python
from toolkit.maintenance import (
    list_python_packages,
    list_duckdb_extensions,
)
list_python_packages()[:10]
list_duckdb_extensions()
```

---

## Installing packages offline (air-gapped servers)

Two steps: download on a machine with internet, copy the files,
install on the offline machine.

### Python package

**On the internet machine:**

```python
from toolkit.maintenance import download_python_package
download_python_package("statsmodels")
# -> saves wheels to offline/wheels/
```

**Copy** the `offline/wheels/` folder to the offline machine.

**On the offline machine:**

```python
from toolkit.maintenance import install_python_package_offline
install_python_package_offline("statsmodels")
```

### DuckDB extension

**On the internet machine:**

```python
from toolkit.maintenance import download_duckdb_extension
download_duckdb_extension("httpfs")
# -> saves to offline/extensions/httpfs.duckdb_extension
```

**Copy** the `.duckdb_extension` file to:

```
runtime/duckdb/extensions/
```

**On the offline machine:**

```python
import duckdb
con = duckdb.connect()
con.execute("SET extension_directory='runtime/duckdb/extensions'")
con.execute("LOAD httpfs")
```

Full guide: `docs/OFFLINE_INSTALL.md`

---

## Teaching the AI about your data

The AI reads three Markdown files through the MCP server:

| File | Purpose | Who edits |
|---|---|---|
| `mcp/context/business.md` | Tables, business rules, metrics | You |
| `mcp/capabilities.md` | What the AI can do, style guide | You |
| `runtime/manifest.md` | Installed packages and extensions | Auto-generated |

### After installing a new package or extension

Run once:

```python
from toolkit.maintenance import refresh_ai_docs
refresh_ai_docs()
```

This regenerates `runtime/manifest.md`. The AI will know about the
new tool the next time it queries.

### After changing your business rules

Just edit `mcp/context/business.md`. The MCP server reads it on every
request, so no restart is needed.

Example addition to `business.md`:

```markdown
## Rules
- All monetary columns are in Iranian Rials (IRR).
- Only `status = 'active'` rows count toward revenue.
```

To see the tips again from Python:

```python
from toolkit.maintenance import show_capabilities_tips
show_capabilities_tips()
```

---

## Local AI assistant

Start it:

```python
from toolkit.ui import start_llama_cpp
start_llama_cpp()
# -> http://localhost:8080
```

Then open the chat panel in JupyterLab.

To switch to a bigger model, see `docs/AI_MODELS.md`. It covers:

- Recommended models (`qwen2.5-3b`, `qwen2.5-7b`, `qwen2.5-coder-7b`)
- Enabling GPU acceleration (NVIDIA CUDA, AMD ROCm, Apple Metal)
- Performance tuning for CPU inference

Quick change:

```python
from toolkit.maintenance import change_ai_model
change_ai_model("qwen2.5-7b")
```

Then restart the server to apply the change:

```python
from toolkit.ui import stop_llama_cpp, start_llama_cpp
stop_llama_cpp()
start_llama_cpp()
```

---

## RAG (give the AI your documents)

See `docs/RAG.md`.

```python
from toolkit.rag import create_index, search
create_index("data/docs", table_name="docs")
search("my question", table_name="docs")
```

---


## Connectors (Kafka, Flink SQL, Trino)

The toolkit includes lightweight Python clients for common
data platforms. No Docker, no local cluster, no PySpark needed.

```python
from toolkit.connections import (
    kafka_consumer, kafka_producer, kafka_topics,
    flink_sql_query, flink_jobs,
    trino_query, trino_catalogs,
)

# Kafka
topics = kafka_topics('kafka-broker:9092')
consumer = kafka_consumer('kafka-broker:9092', topics=['events'])
for msg in consumer:
    print(msg.value)

# Flink SQL Gateway
rows = flink_sql_query(
    'http://flink-sql-gateway:8083',
    'SELECT user_id, COUNT(*) FROM kafka_events GROUP BY user_id',
)

# Trino
df = trino_query(
    host='trino-coordinator',
    sql='SELECT region, COUNT(*) FROM hive.default.sales GROUP BY region',
    catalog='hive',
)
```

| Client | Package | Size |
|---|---|---|
| Kafka (light) | `kafka-python` | ~600 KB |
| Kafka (fast) | `confluent-kafka` | ~5 MB |
| Trino | `trino` | ~2 MB |
| Flink SQL Gateway | `py-flink-sql-gateway` | small |

> **Note:** PySpark is not included by default (~300 MB). Install it
> manually with `runtime/python/python.exe -m pip install pyspark`
> if you need the full Spark DataFrame API.

See [`docs/DATA_ENGINEERING.md`](docs/DATA_ENGINEERING.md) for details.

---


## Online AI models (optional)

In addition to the local llama.cpp model, you can plug in
an online model from **OpenRouter**, **OpenAI**, **Groq**,
**Together**, **DeepSeek**, or any OpenAI-compatible endpoint.

1. Get an API key from your provider
   (e.g. https://openrouter.ai/settings/keys)
2. Edit `config.yaml`:

```yaml
online_ai:
  enabled: true
  provider: "openrouter"
  model: "openai/gpt-4o-mini"
  api_key: "sk-or-v1-..."
  base_url: "https://openrouter.ai/api/v1"
```

3. Call it from Python:

```python
from toolkit.online_ai import chat, list_providers

print(list_providers())                 # built-in presets
print(chat("Explain DuckDB in one line"))
```

The same model is available inside the MCP server as the tool
`online_ai_chat`, so the local AI can delegate hard questions
to the online model.

| Provider | Base URL | Env var |
|---|---|---|
| OpenRouter | https://openrouter.ai/api/v1 | `OPENROUTER_API_KEY` |
| OpenAI | https://api.openai.com/v1 | `OPENAI_API_KEY` |
| Groq | https://api.groq.com/openai/v1 | `GROQ_API_KEY` |
| Together | https://api.together.xyz/v1 | `TOGETHER_API_KEY` |
| DeepSeek | https://api.deepseek.com/v1 | `DEEPSEEK_API_KEY` |

See [`docs/ONLINE_AI.md`](docs/ONLINE_AI.md) for details.

---


## Connectors: Kafka and Trino

The toolkit ships with lightweight Python clients for **Kafka** and
**Trino**. No Docker, no local cluster; point them at any reachable
server on your network.

### Kafka

```python
from toolkit.connections import (
    kafka_topics, kafka_consumer, kafka_producer, kafka_consume_once,
    read_kafka_topic_via_duckdb,
)

# List topics
print(kafka_topics('kafka-broker:9092'))

# Consume (streaming)
consumer = kafka_consumer('kafka-broker:9092', topics=['events'])
for msg in consumer:
    print(msg.topic, msg.partition, msg.offset, msg.value)

# Consume N messages, then stop
rows = kafka_consume_once('kafka-broker:9092', 'events', max_messages=50)

# Produce
producer = kafka_producer('kafka-broker:9092')
producer.send('events', {'user': 'ali', 'action': 'login'})
producer.flush()

# Read a topic as a DuckDB table (no Python client)
import duckdb
con = duckdb.connect()
df = read_kafka_topic_via_duckdb(con, 'kafka-broker:9092', 'events')
```

### Trino

```python
from toolkit.connections import trino_query, trino_catalogs

# List catalogs on a Trino cluster
print(trino_catalogs('trino-coordinator'))

# Run SQL and get a pandas DataFrame
df = trino_query(
    host='trino-coordinator',
    sql='SELECT region, count(*) FROM hive.default.sales GROUP BY region',
    catalog='hive',
    schema='default',
)
print(df)
```

### Client packages

| Client | Package | Size |
|---|---|---|
| Kafka (light) | `kafka-python` | ~600 KB |
| Kafka (fast) | `confluent-kafka` | ~5 MB |
| Trino | `trino` | ~2 MB |

All three are installed with the `standard` and `full` profiles.
Flink SQL is supported through the Flink SQL Gateway REST API
(no Python package needed).

See [`docs/DATA_ENGINEERING.md`](docs/DATA_ENGINEERING.md) for details.

---

## Directory layout

```text
duckdb-toolkit/
├── config.yaml
├── configs/
│   ├── config.light.yaml
│   ├── config.standard.yaml
│   ├── config.full.yaml
│   ├── config.custom.yaml
│   └── secrets.sql
├── setup.py
├── verify.py
├── runtime/                    <- created by setup.py
│   ├── python/                 <- portable Python + packages
│   ├── duckdb/                 <- CLI, extensions, BI drivers
│   ├── llama.cpp/              <- AI engine
│   ├── models/                 <- AI models (GGUF)
│   ├── tiktoken_cache/         <- offline cache for Jupyter AI
│   └── jupyter_config/         <- Jupyter settings
├── toolkit/
│   ├── config.py
│   ├── io_helpers.py
│   ├── parallel.py
│   ├── jobs.py
│   ├── ml.py
│   ├── lakehouse.py
│   ├── ui.py
│   ├── maintenance.py
│   ├── rag.py
│   ├── transcribe.py
│   └── bi_drivers.py
├── examples/                   <- 21 example notebooks
├── dashboards/                 <- 7 Streamlit apps
├── notebooks/                  <- Your own Jupyter notebooks
├── jobs/                       <- Scheduled job scripts
├── mcp/                        <- MCP server for AI
│   ├── server.py
│   ├── manifest_generator.py
│   ├── capabilities.md
│   └── context/
│       └── business.md
├── docs/                       <- User guides
│   ├── index.html              <- Interactive HTML guide
│   ├── INSTALL_LINUX.md
│   ├── CONNECT_DUCK_UI.md
│   ├── CONNECT_BI_TOOLS.md
│   ├── AI_MODELS.md
│   ├── RAG.md
│   ├── OFFLINE_INSTALL.md
│   └── MANIFEST_GENERATOR.md
├── data/                       <- Your data files
├── exports/                    <- Output files
├── reports/                    <- HTML reports
├── mlruns/                     <- MLflow tracking
├── logs/                       <- Job logs
├── offline/                    <- Air-gapped transfers
│   ├── wheels/
│   └── extensions/
│
├── start-jupyter.bat           <- Windows launchers
├── start-jupyter.sh            <- Linux/macOS launchers
├── start-streamlit.bat
└── start-streamlit.sh
```

---

## Uninstall

Delete the project folder. Nothing was installed on the system.

---

## Documentation

- **Launcher scripts**; `setup.bat/.sh`, `verify.bat/.sh`, `start-*.bat/.sh` (see the table above)

- 🌐 **[Interactive HTML guide (live)](https://craftsman-coder.github.io/duckdb-toolkit/)**, open in browser, no download needed
- `docs/INSTALL_LINUX.md` - Linux install
- `docs/CONNECT_DUCK_UI.md` - Offline DuckDB UI
- `docs/AI_MODELS.md` - Switch models, enable GPU
- `docs/RAG.md` - Retrieval-augmented generation
- `docs/OFFLINE_INSTALL.md` - Air-gapped installs
- `docs/MANIFEST_GENERATOR.md` - Environment manifest
- `docs/CONNECT_BI_TOOLS.md` - Connect Tableau, Power BI, Qlik Sense

---

## License

MIT - see the `LICENSE` file.