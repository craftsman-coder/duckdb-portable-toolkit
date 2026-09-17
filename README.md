# Portable DuckDB Toolkit

A fully portable data + ML environment that runs inside Jupyter and
Streamlit. Works on **Windows** and **Linux**. After the initial setup,
everything runs **offline**.

---

## Quick start

### 1. Clone

```bash
git clone https://github.com/YOUR-USERNAME/duckdb-portable-toolkit.git
cd duckdb-portable-toolkit
```

### 2. Run setup (needs internet once)

```bash
python setup.py
```

Choose a profile when asked:

| Option | Profile | Description | Size |
|---|---|---|---|
| 1 | light | DuckDB + Jupyter | ~500 MB |
| 2 | standard | + viz + ML + AI + MCP | ~3-4 GB |
| 3 | full | + EDA + MLflow + all extensions | ~10-12 GB |
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
change_ai_model("qwen3:8b")
```

Then pull the model:

```bash
ollama pull qwen3:8b
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

The default setup uses Ollama with `qwen2.5-coder:3b` on CPU.
Ollama runs fully offline after the model is downloaded once.

Start it:

```python
from toolkit.ui import start_ollama
start_ollama()
```

Then open the chat panel in JupyterLab.

To switch to a bigger model, see `docs/AI_MODELS.md`. It covers:

- Recommended models (`qwen3:8b`, `qwen3:14b`, ...)
- Enabling GPU acceleration (NVIDIA CUDA, AMD ROCm, Apple Metal)
- Using **llama.cpp** instead of Ollama
- Using **vLLM** for high-throughput serving

Quick change:

```python
from toolkit.maintenance import change_ai_model
change_ai_model("qwen3:8b")
```

Then in the terminal:

```bash
ollama pull qwen3:8b
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

## Directory layout

```
duckdb-portable-toolkit/
├── config.yaml
├── configs/
│   ├── config.light.yaml
│   ├── config.standard.yaml
│   ├── config.full.yaml
│   ├── config.custom.yaml
│   └── secrets.sql
├── setup.py
├── verify.py
├── runtime/               <- created by setup.py
│   ├── python/
│   ├── venv/
│   └── duckdb/
├── toolkit/
│   ├── config.py
│   ├── parallel.py
│   ├── jobs.py
│   ├── io_helpers.py
│   ├── ml.py
│   ├── lakehouse.py
│   ├── ui.py
│   ├── maintenance.py     <- user actions
│   └── rag.py
├── examples/
├── dashboards/
├── jobs/
├── mcp/
│   ├── server.py
│   ├── manifest_generator.py
│   ├── capabilities.md
│   └── context/business.md
├── docs/
│   ├── INSTALL_LINUX.md
│   ├── CONNECT_DUCK_UI.md
│   ├── CONNECT_OLLAMA.md
│   ├── MANIFEST_GENERATOR.md
│   ├── AI_MODELS.md
│   ├── RAG.md
│   └── OFFLINE_INSTALL.md
└── offline/               <- for air-gapped transfers
    ├── wheels/
    └── extensions/
```

---

## Uninstall

Delete the project folder. Nothing was installed on the system.

---

## Documentation

- `docs/INSTALL_LINUX.md` - Linux install
- `docs/CONNECT_DUCK_UI.md` - Offline DuckDB UI
- `docs/CONNECT_OLLAMA.md` - Local AI setup
- `docs/AI_MODELS.md` - Switch models, enable GPU
- `docs/RAG.md` - Retrieval-augmented generation
- `docs/OFFLINE_INSTALL.md` - Air-gapped installs
- `docs/MANIFEST_GENERATOR.md` - Environment manifest

---

## License

MIT - see the `LICENSE` file.
