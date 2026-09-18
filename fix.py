#!/usr/bin/env python3
"""
Create the five documentation files in docs/.
Run once:  python create_docs.py
"""

from pathlib import Path

ROOT = Path(__file__).parent.resolve()
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

# Use a marker for triple-backticks to avoid conflicts
BT = "```"


def write(name: str, content: str) -> None:
    path = DOCS / name
    path.write_text(content, encoding="utf-8")
    print(f"  [ok] {path.relative_to(ROOT)}")


# ==================================================================
# 1. INSTALL_LINUX.md
# ==================================================================
INSTALL_LINUX = f"""# Linux Installation Guide

This guide covers installation of the Portable DuckDB Toolkit on
Linux (Ubuntu, Debian, Fedora, Arch, and derivatives).

## Prerequisites

The toolkit installs Python and DuckDB inside the project folder, so
you do NOT need system Python to run the toolkit. However, a system
Python 3.9+ is needed to bootstrap `setup.py`.

### Install system packages

**Debian / Ubuntu:**

{BT}bash
sudo apt update
sudo apt install -y curl wget tar gzip ca-certificates python3
{BT}

**Fedora / RHEL:**

{BT}bash
sudo dnf install -y curl wget tar gzip ca-certificates python3
{BT}

**Arch:**

{BT}bash
sudo pacman -S --needed curl wget tar gzip ca-certificates python
{BT}

### Verify Python

{BT}bash
python3 --version
# Must be 3.9 or newer
{BT}

## Installation

### 1. Clone the repository

{BT}bash
git clone https://github.com/YOUR-USERNAME/duckdb-portable-toolkit.git
cd duckdb-portable-toolkit
{BT}

### 2. Run the setup script

{BT}bash
python3 setup.py
{BT}

Choose a profile:

| # | Profile | Size |
|---|---|---|
| 1 | light | ~500 MB |
| 2 | standard | ~3-4 GB |
| 3 | full | ~10-12 GB |
| 4 | custom | varies |

Or skip the prompt:

{BT}bash
python3 setup.py --profile standard
{BT}

### 3. Verify installation

{BT}bash
python3 verify.py
{BT}

All checks should show `[ok]`. If any fail, re-run `python3 setup.py`.

## Running the toolkit

### Launch JupyterLab

{BT}bash
chmod +x start-jupyter.sh   # first time only
./start-jupyter.sh
{BT}

Or from the terminal directly:

{BT}bash
runtime/python/bin/python3 -m jupyterlab --ip=0.0.0.0 --port=8888
{BT}

- `--ip=0.0.0.0` makes it accessible from other machines on the LAN
- Remove it to bind to localhost only

Then open `http://localhost:8888` in your browser.

### Launch a Streamlit dashboard

{BT}bash
chmod +x start-streamlit.sh
./start-streamlit.sh
{BT}

Or directly:

{BT}bash
runtime/python/bin/python3 -m streamlit run \\
    dashboards/01_orders_dashboard.py \\
    --server.port 8501 \\
    --server.address 0.0.0.0
{BT}

### DuckDB CLI

{BT}bash
runtime/duckdb/duckdb my_database.duckdb
{BT}

### Run manifest generator

{BT}bash
runtime/python/bin/python3 mcp/manifest_generator.py
{BT}

## Networking

### Access from another machine on the LAN

1. Bind to `0.0.0.0` (see commands above)
2. Find your IP:

   {BT}bash
   ip addr show | grep "inet "
   # or
   hostname -I
   {BT}

3. Open the firewall (if `ufw` is active):

   {BT}bash
   sudo ufw allow 8888/tcp      # JupyterLab
   sudo ufw allow 8501/tcp      # Streamlit
   sudo ufw allow 5522/tcp      # duck-ui
   sudo ufw allow 8080/tcp      # llama.cpp server
   {BT}

4. Colleagues open `http://YOUR-IP:8888/lab` in their browser.

### SSH tunnel (safer alternative)

{BT}bash
# On your local machine
ssh -L 8888:localhost:8888 user@server
{BT}

Then open `http://localhost:8888/lab` locally.

## Running in the background

### Using `nohup`

{BT}bash
nohup ./start-jupyter.sh > logs/jupyter.log 2>&1 &
{BT}

### Using `systemd` (permanent service)

Create `/etc/systemd/system/duckdb-toolkit.service`:

{BT}ini
[Unit]
Description=Portable DuckDB Toolkit - JupyterLab
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/home/YOUR_USER/duckdb-portable-toolkit
ExecStart=/home/YOUR_USER/duckdb-portable-toolkit/runtime/python/bin/python3 -m jupyterlab --ip=0.0.0.0 --port=8888 --no-browser
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
{BT}

Enable and start:

{BT}bash
sudo systemctl daemon-reload
sudo systemctl enable duckdb-toolkit
sudo systemctl start duckdb-toolkit
sudo systemctl status duckdb-toolkit
{BT}

## Common Issues

### Permission denied on scripts

{BT}bash
chmod +x start-jupyter.sh start-streamlit.sh
chmod +x runtime/python/bin/*
chmod +x runtime/duckdb/duckdb
{BT}

### Missing shared libraries

{BT}bash
# Debian / Ubuntu
sudo apt install -y libpython3-dev

# Fedora
sudo dnf install -y python3-devel
{BT}

### Port already in use

{BT}bash
sudo lsof -i :8888
sudo netstat -tlnp | grep 8888
kill -9 <PID>
{BT}

### Network download slow

{BT}bash
curl -I https://github.com
curl -I https://pypi.org
python3 setup.py
{BT}

Already-installed components are skipped (`skip_existing: true`).

## Uninstall

{BT}bash
cd ..
rm -rf duckdb-portable-toolkit
{BT}

## Next Steps

- [Connecting to duck-ui](CONNECT_DUCK_UI.md)
- [Local AI with llama.cpp](AI_MODELS.md)
- [RAG with your documents](RAG.md)
- [Offline installation](OFFLINE_INSTALL.md)
"""


# ==================================================================
# 2. CONNECT_DUCK_UI.md
# ==================================================================
CONNECT_DUCK_UI = f"""# Connecting to duck-ui

`duck-ui` is a fully offline web interface for DuckDB. It runs in a
Docker container and lets you explore databases, run SQL, and
visualize data in your browser.

## Why use duck-ui?

- Quick data exploration without writing code
- Full-featured SQL editor with syntax highlighting
- Built-in simple charts (bar, line, pie)
- Works fully offline
- Complements JupyterLab (which is better for scripting)

## Requirements

**Docker** installed and running.

### Install Docker

**Windows / macOS:**

Download Docker Desktop from
[https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
and run the installer.

**Linux (Debian / Ubuntu):**

{BT}bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
{BT}

**Linux (Fedora):**

{BT}bash
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
{BT}

### Verify Docker

{BT}bash
docker --version
docker ps
{BT}

## Starting duck-ui

### From JupyterLab (recommended)

{BT}python
from toolkit.ui import start_duck_ui
url = start_duck_ui()
print(url)
{BT}

Output:

{BT}text
duck-ui is running at http://localhost:5522
http://localhost:5522
{BT}

Then open `http://localhost:5522` in your browser.

### From a terminal

{BT}bash
docker run -d --rm \\
  --name duck-ui \\
  -p 5522:5522 \\
  ghcr.io/caioricciuti/duck-ui:latest
{BT}

### Change the port

{BT}python
from toolkit.ui import start_duck_ui
start_duck_ui(port=5523)
{BT}

### Custom image version

{BT}python
start_duck_ui(image="ghcr.io/caioricciuti/duck-ui:v1.2.0")
{BT}

## Using duck-ui

### 1. Connect to a DuckDB database

In duck-ui, click **New Connection** and enter:

- **Database path:** `runtime/duckdb/your_db.duckdb`
  (or any `.duckdb` file in the project)
- **Read-only:** check this box for safety

### 2. Upload a Parquet or CSV file

Drag and drop a file into the interface, or use the file picker.

### 3. Run SQL

{BT}sql
SELECT
    DATE_TRUNC('month', sale_date) AS month,
    SUM(amount) AS revenue
FROM sales
WHERE status = 'active'
GROUP BY 1
ORDER BY 1;
{BT}

### 4. Save queries

Use the **Save** button to keep frequently-used queries for later.

## Stopping duck-ui

### From Python

{BT}python
from toolkit.ui import stop_duck_ui
stop_duck_ui()
{BT}

### From terminal

{BT}bash
docker stop duck-ui
{BT}

## Offline Operation

duck-ui works fully offline:

- The container image is pulled once (needs internet)
- After that, everything is local
- No data leaves your machine

**Verify offline operation:**

1. Start duck-ui
2. Disconnect from the internet
3. Open `http://localhost:5522` — it should still work

## Persistent storage (optional)

{BT}bash
docker run -d --rm \\
  --name duck-ui \\
  -p 5522:5522 \\
  -v "$(pwd)/runtime/duck-ui-data:/data" \\
  ghcr.io/caioricciuti/duck-ui:latest
{BT}

## Comparison with JupyterLab

| Feature | JupyterLab | duck-ui |
|---|---|---|
| Writing analysis code | Yes | Limited |
| SQL editor | Basic (jupysql) | Full-featured |
| Charts | All Python libs | Built-in simple charts |
| Notebooks | Yes | No |
| Data preview | `df.head()` | Interactive table |
| Script automation | Yes | No |
| Quick exploration | Medium | Fast |

**Use both:**

- duck-ui for quick data exploration and ad-hoc SQL
- JupyterLab for pipelines, ML, and reports

## Troubleshooting

### Docker daemon not running

- **Windows / macOS:** Start Docker Desktop from the Start menu
- **Linux:** `sudo systemctl start docker`

### Port 5522 already in use

{BT}python
start_duck_ui(port=5523)
{BT}

### Container starts but page doesn't load

{BT}bash
docker ps
docker logs duck-ui
docker stop duck-ui
docker run -d --rm --name duck-ui -p 5522:5522 \\
  ghcr.io/caioricciuti/duck-ui:latest
{BT}

### "Cannot connect to Docker daemon"

{BT}bash
groups | grep docker
sudo usermod -aG docker $USER
{BT}

### Pull fails (offline)

On a machine with internet:

{BT}bash
docker pull ghcr.io/caioricciuti/duck-ui:latest
docker save ghcr.io/caioricciuti/duck-ui:latest -o duck-ui.tar
{BT}

Copy `duck-ui.tar` to the offline machine and load it:

{BT}bash
docker load -i duck-ui.tar
{BT}

## Next Steps

- [Local AI with llama.cpp](AI_MODELS.md)
- [RAG with your documents](RAG.md)
- [Offline installation](OFFLINE_INSTALL.md)
"""


# ==================================================================
# 3. AI_MODELS.md
# ==================================================================
AI_MODELS = f"""# AI Models with llama.cpp

The toolkit uses **llama.cpp** as its local AI engine. It's fully
portable, lightweight (~89 MB binary), and runs on CPU without a GPU.

The default model is **Qwen2.5-1.5B-Instruct** (Q4_K_M quantized, ~1 GB).

## Why llama.cpp over Ollama?

| Feature | llama.cpp | Ollama |
|---|---|---|
| Binary size | ~89 MB | ~680 MB |
| Startup time | 1-2 sec | 5-10 sec |
| RAM usage | ~100 MB | ~200+ MB |
| Portable | Yes | No |
| No background service | Yes | No |
| OpenAI-compatible API | Yes | Partial |

## Available models

In a Jupyter cell:

{BT}python
from toolkit.maintenance import list_ai_models
list_ai_models()
{BT}

Output:

{BT}text
Name                     Size     Notes
------------------------------------------------------------------
qwen2.5-1.5b           1.0 GB   Fast, good for CPU. Recommended default.
qwen2.5-3b             2.0 GB   Better quality, needs 8 GB RAM.
qwen2.5-7b             4.5 GB   Best quality on CPU, needs 16 GB RAM.
qwen2.5-coder-1.5b     1.0 GB   Optimized for code. Very fast.
qwen2.5-coder-7b       4.5 GB   Best code model, needs 16 GB RAM.
tinyllama-1.1b         0.7 GB   Ultra-light, works on any CPU.
{BT}

## Switch to a different model

{BT}python
from toolkit.maintenance import change_ai_model
change_ai_model("qwen2.5-7b")
{BT}

This will:

1. Download the GGUF file to `runtime/models/`
2. Update `config.yaml` with the new filename and URL
3. Print instructions to restart the server

Then restart the server:

{BT}python
from toolkit.ui import stop_llama_cpp, start_llama_cpp
stop_llama_cpp()
start_llama_cpp()
{BT}

## Download only (without switching)

{BT}python
from toolkit.maintenance import download_ai_model
download_ai_model("qwen2.5-coder-7b")
{BT}

Useful if you want the model available for later but keep the current
one active for now.

## Use a custom GGUF model

1. Copy the file to `runtime/models/`:

   {BT}text
   runtime/models/my-model.gguf
   {BT}

2. Edit `config.yaml`:

   {BT}yaml
   ai:
     model:
       dir: "runtime/models"
       filename: "my-model.gguf"
       download_url: ""
   {BT}

3. Restart the server.

## GPU acceleration

Set the number of layers offloaded to GPU in `config.yaml`:

{BT}yaml
ai:
  server:
    n_gpu_layers: 999    # 0 = CPU only; 999 = all layers on GPU
{BT}

Restart the server after changing this.

### Requirements by GPU vendor

| GPU | Requirements |
|---|---|
| NVIDIA | CUDA 12.x, latest driver |
| AMD | ROCm 5.6+ |
| Apple Silicon | macOS 13+ (Metal built in) |
| Intel Arc | oneAPI |

### Verify GPU is used

**NVIDIA:**

{BT}bash
nvidia-smi
# Look for llama-server in the process list
{BT}

**AMD:**

{BT}bash
rocm-smi
{BT}

For CPU-only setups (the default), leave `n_gpu_layers: 0`.

## Performance on CPU

| Model | Speed | RAM needed |
|---|---|---|
| tinyllama-1.1b | ~25 tok/s | 2 GB |
| qwen2.5-1.5b | ~15 tok/s | 3 GB |
| qwen2.5-3b | ~8 tok/s | 6 GB |
| qwen2.5-7b | ~3 tok/s | 12 GB |

### Tips to speed up CPU inference

1. Increase threads in `config.yaml` (match CPU cores)
2. Reduce `ctx_size` if you don't need long context
3. Close other applications to free RAM

## Server options

{BT}yaml
ai:
  server:
    threads: 4          # CPU threads
    ctx_size: 2048      # context window in tokens
    batch_size: 512     # prompt batch size
    n_gpu_layers: 0     # 0 = CPU only
{BT}

Restart the server after any change.

## Managing the server

### Start

{BT}python
from toolkit.ui import start_llama_cpp
start_llama_cpp()
# -> http://localhost:8080
{BT}

### Stop

{BT}python
from toolkit.ui import stop_llama_cpp
stop_llama_cpp()
{BT}

### Check status

{BT}python
import urllib.request
try:
    urllib.request.urlopen("http://localhost:8080/v1/models", timeout=2)
    print("Server is running")
except Exception:
    print("Server is not running")
{BT}

## Connect Jupyter AI

In JupyterLab, open **Settings -> Settings Editor -> Jupyter AI**:

- **Provider:** `Generic (OpenAI-compatible)`
- **Base URL:** `http://localhost:8080/v1`
- **API key:** (leave empty)
- **Model:** the filename without `.gguf`

Then open the chat panel (left sidebar) and start asking questions.

## Command-line usage

{BT}bash
# Windows
runtime\\llama.cpp\\llama-server.exe ^
    -m runtime\\models\\qwen2.5-1.5b-instruct-q4_k_m.gguf ^
    --port 8080

# Linux / macOS
runtime/llama.cpp/llama-server \\
    -m runtime/models/qwen2.5-1.5b-instruct-q4_k_m.gguf \\
    --port 8080
{BT}

## Troubleshooting

### "llama-server not found"

Run `python setup.py` to download llama.cpp.

### "Model not found"

Run `python setup.py` or:

{BT}python
from toolkit.maintenance import download_ai_model
download_ai_model("qwen2.5-1.5b")
{BT}

### Server starts but Jupyter AI cannot connect

- Verify the URL: `http://localhost:8080/v1`
- Check that port 8080 is not used by another process

### Slow responses

- Use a smaller model
- Increase `threads` in `config.yaml`
- Reduce `ctx_size`

### Out of memory

- Use a smaller model
- Reduce `ctx_size` and `batch_size`

### GPU not detected

- Verify driver: `nvidia-smi` (NVIDIA) or `rocm-smi` (AMD)
- Restart the server after installing drivers

## Next Steps

- [RAG with your documents](RAG.md)
- [MCP Server for AI](../mcp/capabilities.md)
- [Offline installation](OFFLINE_INSTALL.md)
"""


# ==================================================================
# 4. RAG.md
# ==================================================================
RAG = f"""# Retrieval-Augmented Generation (RAG)

Give your local AI access to your own documents: business rules, PDF
extracts, markdown notes, CSV headers, SQL schemas — anything in text
form. The AI will search this library before answering.

Everything runs **offline** after the embedding model is downloaded.

## How it works

1. **Chunk** documents into ~500-character pieces.
2. **Embed** each chunk with `sentence-transformers/all-MiniLM-L6-v2`
   (a 90 MB model that runs on CPU in milliseconds).
3. **Store** the embeddings in a DuckDB table with a VSS (vector) index.
4. **Search** with cosine similarity when the user asks a question.
5. **Inject** the top-k chunks into the AI prompt.

## 1. Prepare your documents

Create a folder, e.g. `data/docs/`:

{BT}text
data/docs/
├── business_rules.md
├── schema_notes.md
├── glossary.md
└── policies/
    ├── returns.md
    └── refunds.md
{BT}

Plain text, Markdown, reStructuredText, and JSON are supported.

## 2. Build the index

{BT}python
from toolkit.rag import create_index

create_index(
    docs_dir="data/docs",
    table_name="my_knowledge",
    db_path="runtime/rag.duckdb",
)
{BT}

The first run downloads the embedding model (~90 MB), then chunks,
embeds, and stores everything.

## 3. Search

{BT}python
from toolkit.rag import search

results = search("How do refunds work?", table_name="my_knowledge", k=3)
for r in results:
    print(f"[{{r['score']:.3f}}] {{r['source']}}")
    print(r["text"][:200])
    print("---")
{BT}

Each result has:

- `source` — the file it came from
- `text` — the chunk content
- `score` — cosine similarity (higher = more relevant)

## 4. Feed results to your AI

### Option A: Copy the prompt manually

{BT}python
from toolkit.rag import build_prompt

prompt = build_prompt("How do refunds work?", table_name="my_knowledge", k=5)
print(prompt)
# Copy the printed prompt into your Jupyter AI chat panel
{BT}

### Option B: Let the MCP server do it

Add a tool to `mcp/server.py` that calls `toolkit.rag.search`:

{BT}python
@app.call_tool()
async def call_tool(name, arguments):
    ...
    if name == "rag_search":
        query = arguments.get("query", "")
        from toolkit.rag import search
        hits = search(query, table_name="my_knowledge", k=5)
        return [TextContent(type="text",
                            text=json.dumps(hits, indent=2, ensure_ascii=False))]
{BT}

Now the AI can call `rag_search("...")` on its own.

### Option C: Jupyter AI inline

{BT}text
Use this context to answer:

<context>
... (paste build_prompt output) ...
</context>

Question: How do refunds work?
{BT}

## 5. Keep the index fresh

{BT}python
from toolkit.rag import create_index
create_index("data/docs", table_name="my_knowledge")
{BT}

It drops and rebuilds the table, so it's always up to date.

### Incremental update (advanced)

{BT}python
import duckdb
from pathlib import Path
from toolkit.config import EXTENSIONS_DIR

con = duckdb.connect("runtime/rag.duckdb")
con.execute(f"SET extension_directory='{{EXTENSIONS_DIR}}'; LOAD vss;")

existing = set(row[0] for row in con.execute(
    "SELECT DISTINCT source FROM my_knowledge"
).fetchall())

current = set(
    str(p.relative_to("data/docs"))
    for p in Path("data/docs").rglob("*") if p.is_file()
)

new = current - existing
removed = existing - current
print("new:", new)
print("removed:", removed)
{BT}

## 6. Tuning

### Chunk size

{BT}python
create_index("data/docs", chunk_size=800, chunk_overlap=100)
{BT}

- Larger chunks = more context per hit, fewer hits
- Smaller chunks = more precise, but might miss context

Recommended: **500-800 characters** for prose, **300** for code.

### Number of results

{BT}python
search("...", k=10)   # more context
search("...", k=3)    # less noise
{BT}

Recommended: **3-5**.

### Different embedding model

{BT}python
create_index(
    "data/docs",
    model_name="sentence-transformers/all-mpnet-base-v2",
)
{BT}

| Model | Size | Speed | Quality |
|---|---|---|---|
| all-MiniLM-L6-v2 | 90 MB | Fastest | Good |
| all-mpnet-base-v2 | 420 MB | Medium | Better |
| BAAI/bge-small-en-v1.5 | 130 MB | Fast | Very good |
| BAAI/bge-large-en-v1.5 | 1.3 GB | Slow | Best |

If you switch models, you must re-index.

## 7. Multilingual documents

For Persian, Arabic, or other non-English documents:

{BT}python
create_index(
    "data/docs",
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
{BT}

For mixed Persian + English, use `paraphrase-multilingual-MiniLM-L12-v2`
or `BAAI/bge-m3`.

## 8. Example end-to-end

{BT}python
from toolkit.rag import create_index, search
from toolkit.ui import start_llama_cpp

# 1. Build the index once
create_index("mcp/context", table_name="business")
create_index("data/docs",     table_name="policies")

# 2. Start the AI
start_llama_cpp()

# 3. Ask a question
q = "What's our return policy for wholesale customers?"
ctx1 = search(q, table_name="business", k=3)
ctx2 = search(q, table_name="policies", k=3)

prompt = (
    "Answer using the context below:\\n\\n"
    + "\\n\\n".join(r["text"] for r in ctx1 + ctx2)
    + f"\\n\\nQuestion: {{q}}"
)
print(prompt)
# Paste into Jupyter AI chat
{BT}

## 9. Troubleshooting

### "model not found"

The embedding model must be downloaded once (needs internet).
After that it's cached in `~/.cache/huggingface/`.

### "vss extension not found"

{BT}python
from toolkit.maintenance import install_duckdb_extension
install_duckdb_extension("vss")
{BT}

### Search returns garbage

- Documents may be too short or too long
- Try different `chunk_size`
- Check that the query language matches the documents

### Slow first query

The embedding model loads into RAM (~90 MB for MiniLM).
Subsequent queries are much faster.

## 10. What to put in your docs

**Good candidates:**

- Business rules and definitions
- Data dictionary / column meanings
- Team conventions (naming, style)
- SQL snippets that worked
- Frequently-asked questions from colleagues

**Avoid:**

- Large PDFs without conversion (use `pdfplumber` first)
- Binary files
- Highly dynamic data (put that in DuckDB tables, not RAG)

## Next Steps

- [Local AI with llama.cpp](AI_MODELS.md)
- [MCP Server for AI](../mcp/capabilities.md)
- [Offline installation](OFFLINE_INSTALL.md)
"""


# ==================================================================
# 5. MANIFEST_GENERATOR.md
# ==================================================================
MANIFEST_GENERATOR = f"""# Manifest Generator

The `mcp/manifest_generator.py` script creates `runtime/manifest.md`:
a snapshot of everything installed in your environment. The AI reads
this through the MCP server to know what tools are available.

## When to Run

- **After `setup.py`** — automatic (no action needed)
- **After installing new packages** — manually
- **After installing new DuckDB extensions** — manually
- **Before starting work with AI** — for safety

## How to Run

### Windows (PowerShell or CMD)

{BT}cmd
runtime\\python\\python.exe mcp\\manifest_generator.py
{BT}

### Linux / macOS / Git Bash

{BT}bash
runtime/python/bin/python3 mcp/manifest_generator.py
{BT}

Note: in Git Bash on Windows, use forward slashes:

{BT}bash
runtime/python/python.exe mcp/manifest_generator.py
{BT}

### From Jupyter

In any notebook cell:

{BT}python
%run mcp/manifest_generator.py
{BT}

Or:

{BT}python
import importlib
import mcp.manifest_generator as mg
importlib.reload(mg)
mg.main()
{BT}

## Output

The script writes `runtime/manifest.md`:

{BT}markdown
# Environment Manifest

Generated: 2026-09-18T11:30:22
OS: Windows 11
Architecture: AMD64

## Python packages

| Package | Version |
|---|---|
| duckdb | 1.5.5 |
| pandas | 2.3.3 |
| numpy | 2.3.5 |
| jupyterlab | 4.6.3 |

## DuckDB

- Version: **1.5.5**

## DuckDB extensions

| Extension | Description |
|---|---|
| iceberg | Iceberg table support |
| delta | Delta Lake support |
| oracle_scanner | Query Oracle databases |

## Toolkit helper modules

- `toolkit.config`
- `toolkit.io_helpers`
- `toolkit.jobs`
- `toolkit.lakehouse`
- `toolkit.maintenance`
- `toolkit.ml`
- `toolkit.parallel`
- `toolkit.rag`
- `toolkit.transcribe`
- `toolkit.ui`
{BT}

## How the AI Uses It

The MCP server exposes the manifest as a tool:

{BT}python
environment_manifest()
{BT}

When the AI needs to know what's installed, it calls this tool and
receives the Markdown content. This prevents the AI from suggesting
packages that aren't installed.

**Example conversation:**

> **You:** Write a script to profile a DataFrame.
>
> **AI (thinking):** Let me check what's installed.
> → calls `environment_manifest()`
> → sees `ydata-profiling` in the list
> **AI:** Here's a script using ydata-profiling...

## Automating It

### Git hook (Linux / macOS)

Add to `.git/hooks/post-merge`:

{BT}bash
#!/bin/sh
cd "$(git rev-parse --show-toplevel)"
runtime/python/bin/python3 mcp/manifest_generator.py
{BT}

Make it executable:

{BT}bash
chmod +x .git/hooks/post-merge
{BT}

### Alias (any OS)

Add to `~/.bashrc` (Linux) or `~/.bash_profile`:

{BT}bash
alias refresh-manifest='cd ~/duckdb-portable-toolkit && runtime/python/bin/python3 mcp/manifest_generator.py'
{BT}

### From Python (in a notebook)

{BT}python
from toolkit.maintenance import refresh_ai_docs
refresh_ai_docs()
{BT}

This is the simplest option — call it after any install.

## What It Reads

The manifest generator inspects:

1. **Python packages** — via `pip list --format=json`
2. **DuckDB version** — by importing `duckdb` in the portable Python
3. **DuckDB extensions** — by querying `duckdb_extensions()`
4. **Toolkit modules** — by listing `toolkit/*.py`

## Troubleshooting

### "No packages found"

This means the manifest generator couldn't find the portable Python.
Check that `runtime/python/python.exe` (or `runtime/python/bin/python3`)
exists.

If you recently moved the project, the `.pth` file that registers the
toolkit path may be stale. Re-run:

{BT}bash
python setup.py
{BT}

### Manifest not updating

Check the modification time:

{BT}bash
ls -la runtime/manifest.md      # Linux / macOS / Git Bash
dir runtime\\manifest.md         # Windows
{BT}

If it's old, the generator didn't run. Run it manually.

### AI doesn't see new packages

The MCP server reads `runtime/manifest.md` on every request. If it's
not updating, the file might be cached by the AI. Try:

1. Regenerate the manifest
2. Restart the MCP client (or JupyterLab)
3. Ask the AI to call `environment_manifest()` again

## Manual Editing

The manifest is auto-generated — **don't edit it by hand**. Any
changes will be overwritten the next time the generator runs.

If you want to add custom notes for the AI, edit
`mcp/capabilities.md` instead.

## Next Steps

- [AI Models](AI_MODELS.md)
- [MCP Capabilities](../mcp/capabilities.md)
- [RAG](RAG.md)
"""


# ==================================================================
# Main
# ==================================================================
def main() -> None:
    print()
    print("=" * 60)
    print("  Creating documentation files")
    print("=" * 60)
    print()

    write("INSTALL_LINUX.md", INSTALL_LINUX)
    write("CONNECT_DUCK_UI.md", CONNECT_DUCK_UI)
    write("AI_MODELS.md", AI_MODELS)
    write("RAG.md", RAG)
    write("MANIFEST_GENERATOR.md", MANIFEST_GENERATOR)

    print()
    print("=" * 60)
    print("  Done.")
    print("=" * 60)
    print()
    print("  Files created in docs/")
    print()
    print("  Next:")
    print("    git add docs/")
    print('    git commit -m "docs: add five user guides"')
    print("    git push")
    print()


if __name__ == "__main__":
    main()