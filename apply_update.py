#!/usr/bin/env python3
"""
Apply focused updates to the Portable DuckDB Toolkit.

This script ONLY does the following:
  1. Replaces the banner in setup.py with a clear ASCII logo
  2. Creates toolkit/maintenance.py
  3. Creates docs/OFFLINE_INSTALL.md
  4. Rewrites README.md

Nothing else is touched.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
SQ = "@SQ@"
DQ = "@DQ@"


def m(s: str) -> str:
    return s.replace(SQ, "'''").replace(DQ, '"""')


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(m(content), encoding="utf-8")
    print(f"  [ok] {path.relative_to(ROOT)}")


# ==================================================================
# 1. Fix the banner in setup.py
# ==================================================================
NEW_BANNER = r'''        banner = r@SQ@
  ____             _         ____  ____
 |  _ \ _   _  ___| | __    |  _ \| __ )
 | | | | | | |/ __| |/ /    | | | |  _ \
 | |_| | |_| | (__|   <     | |_| | |_) |
 |____/ \__,_|\___|_|\_\    |____/|____/

        p o r t a b l e   t o o l k i t
@SQ@
'''


def fix_setup_banner() -> None:
    setup_file = ROOT / "setup.py"
    if not setup_file.exists():
        print("  [!!] setup.py not found, skipping banner fix")
        return

    content = setup_file.read_text(encoding="utf-8")

    pattern = re.compile(
        r"        banner = r'''[\s\S]*?'''\n",
        re.MULTILINE,
    )
    if not pattern.search(content):
        print("  [!!] could not locate banner in setup.py")
        return

    content = pattern.sub(m(NEW_BANNER), content, count=1)
    setup_file.write_text(content, encoding="utf-8")
    print("  [ok] setup.py banner replaced")


# ==================================================================
# 2. toolkit/maintenance.py
# ==================================================================
def write_maintenance() -> None:
    content = r'''@DQ@
User-friendly maintenance functions.

Use these inside a Jupyter notebook to:

  - install a new Python package (online or offline)
  - install a new DuckDB extension (online or offline)
  - download a package/extension for use on an offline machine
  - change the AI model in config.yaml
  - refresh the AI-visible manifest

All functions use the portable venv and portable DuckDB, so they
work without touching the system Python.
@DQ@

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from toolkit.config import (
    DUCKDB_EXE,
    EXTENSIONS_DIR,
    ROOT_DIR,
    VENV_DIR,
)


# ------------------------------------------------------------------
# Internal paths
# ------------------------------------------------------------------
def _venv_pip() -> Path:
    return (VENV_DIR / "Scripts" / "pip.exe" if sys.platform == "win32"
            else VENV_DIR / "bin" / "pip")


def _venv_python() -> Path:
    return (VENV_DIR / "Scripts" / "python.exe" if sys.platform == "win32"
            else VENV_DIR / "bin" / "python")


def _manifest_script() -> Path:
    return ROOT_DIR / "mcp" / "manifest_generator.py"


def _config_file() -> Path:
    return ROOT_DIR / "config.yaml"


# ==================================================================
# Python packages
# ==================================================================
def install_python_package(package: str) -> bool:
    @DQ@
    Install a Python package into the portable venv.

    Example:
        install_python_package("statsmodels")
        install_python_package("seaborn==0.13.2")
    @DQ@
    pip = _venv_pip()
    if not pip.exists():
        print(f"pip not found at {pip}. Run setup.py first.")
        return False

    print(f"Installing {package} ...")
    r = subprocess.run(
        [str(pip), "install", "--no-warn-script-location",
         "--disable-pip-version-check", "--timeout", "120", package],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        print(f"  [ok] {package} installed")
        refresh_ai_docs()
        return True
    print(f"  [XX] {package} failed")
    if r.stderr:
        print("       " + r.stderr.strip().splitlines()[-1])
    return False


def list_python_packages() -> list[dict]:
    @DQ@Return a list of installed Python packages as {name, version}.@DQ@
    import json
    py = _venv_python()
    if not py.exists():
        return []
    r = subprocess.run([str(py), "-m", "pip", "list", "--format=json"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return []
    try:
        return json.loads(r.stdout)
    except Exception:
        return []


# ==================================================================
# Offline: download / install Python packages
# ==================================================================
def download_python_package(package: str,
                            dest: Path | str = "offline/wheels") -> bool:
    @DQ@
    Download a package and all its dependencies as wheels.

    Run this on a machine WITH internet, then copy the folder to the
    offline machine and use install_python_package_offline().

    Example:
        download_python_package("statsmodels")
    @DQ@
    dest = Path(dest)
    if not dest.is_absolute():
        dest = ROOT_DIR / dest
    dest.mkdir(parents=True, exist_ok=True)

    pip = _venv_pip()
    if not pip.exists():
        print(f"pip not found at {pip}.")
        return False

    print(f"Downloading {package} to {dest} ...")
    r = subprocess.run(
        [str(pip), "download", package, "-d", str(dest)],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        print(f"  [ok] wheels saved to {dest}")
        print(f"       Copy this folder to the offline machine,")
        print(f"       then run install_python_package_offline('{package}')")
        return True
    print(f"  [XX] download failed")
    if r.stderr:
        print("       " + r.stderr.strip().splitlines()[-1])
    return False


def install_python_package_offline(
    package: str,
    source: Path | str = "offline/wheels",
) -> bool:
    @DQ@
    Install a Python package from a local folder of wheels (no internet).

    Example:
        install_python_package_offline("statsmodels")
    @DQ@
    src = Path(source)
    if not src.is_absolute():
        src = ROOT_DIR / src
    if not src.exists():
        print(f"Folder not found: {src}")
        print("Did you download the wheels first?")
        return False

    pip = _venv_pip()
    if not pip.exists():
        print(f"pip not found at {pip}.")
        return False

    print(f"Installing {package} from {src} ...")
    r = subprocess.run(
        [str(pip), "install", "--no-index",
         f"--find-links={src}", package,
         "--no-warn-script-location",
         "--disable-pip-version-check"],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        print(f"  [ok] {package} installed offline")
        refresh_ai_docs()
        return True
    print(f"  [XX] install failed")
    if r.stderr:
        print("       " + r.stderr.strip().splitlines()[-1])
    return False


# ==================================================================
# DuckDB extensions
# ==================================================================
def install_duckdb_extension(name: str, community: bool = False) -> bool:
    @DQ@
    Install a DuckDB extension into the portable extension folder.

    Example:
        install_duckdb_extension("httpfs")
        install_duckdb_extension("qvd", community=True)
    @DQ@
    if not DUCKDB_EXE.exists():
        print(f"DuckDB CLI not found at {DUCKDB_EXE}.")
        return False

    src = "FROM community" if community else ""
    sql = (f"SET extension_directory='{EXTENSIONS_DIR}'; "
           f"INSTALL {name} {src};")
    print(f"Installing DuckDB extension: {name} ...")
    r = subprocess.run([str(DUCKDB_EXE), "-c", sql],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  [ok] {name} installed")
        refresh_ai_docs()
        return True
    print(f"  [XX] {name} failed")
    if r.stderr:
        print("       " + r.stderr.strip().splitlines()[-1])
    return False


def list_duckdb_extensions() -> list[dict]:
    @DQ@List installed DuckDB extensions.@DQ@
    import json
    if not DUCKDB_EXE.exists():
        return []
    sql = (f"SET extension_directory='{EXTENSIONS_DIR}'; "
           "SELECT extension_name, description "
           "FROM duckdb_extensions() WHERE installed "
           "ORDER BY extension_name;")
    r = subprocess.run([str(DUCKDB_EXE), "-json", "-c", sql],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return []
    try:
        return json.loads(r.stdout)
    except Exception:
        return []


# ==================================================================
# Offline: download DuckDB extensions
# ==================================================================
def download_duckdb_extension(
    name: str,
    dest: Path | str = "offline/extensions",
    community: bool = False,
) -> bool:
    @DQ@
    Download a DuckDB extension as a .duckdb_extension file.

    Run this on a machine WITH internet, then copy the file to the
    offline machine's runtime/duckdb/extensions/ folder.

    Example:
        download_duckdb_extension("httpfs")
        download_duckdb_extension("qvd", community=True)
    @DQ@
    dest = Path(dest)
    if not dest.is_absolute():
        dest = ROOT_DIR / dest
    dest.mkdir(parents=True, exist_ok=True)

    if not DUCKDB_EXE.exists():
        print(f"DuckDB CLI not found at {DUCKDB_EXE}.")
        return False

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        src = "FROM community" if community else ""
        sql = (f"SET extension_directory='{tmp_path}'; "
               f"INSTALL {name} {src};")
        print(f"Downloading DuckDB extension: {name} ...")
        r = subprocess.run([str(DUCKDB_EXE), "-c", sql],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  [XX] download failed")
            if r.stderr:
                print("       " + r.stderr.strip().splitlines()[-1])
            return False

        found = False
        for f in tmp_path.rglob("*.duckdb_extension"):
            shutil.copy2(f, dest / f.name)
            print(f"  [ok] saved {dest / f.name}")
            found = True
            break
        if not found:
            print("  [XX] extension file not found after install")
            return False

    print()
    print("  On the OFFLINE machine, copy the .duckdb_extension file to:")
    print(f"     {EXTENSIONS_DIR}")
    print("  Then load it with:")
    print(f"     LOAD {name};")
    return True


# ==================================================================
# AI model switching
# ==================================================================
def change_ai_model(model_name: str) -> bool:
    @DQ@
    Change the AI model in config.yaml.

    Example:
        change_ai_model("qwen2.5-coder:7b")
        change_ai_model("qwen3:8b")
    @DQ@
    cfg_file = _config_file()
    if not cfg_file.exists():
        print(f"Config file not found: {cfg_file}")
        return False

    try:
        import yaml
    except ImportError:
        print("PyYAML not available in this session.")
        return False

    text = cfg_file.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}

    if "ai" not in data:
        data["ai"] = {}
    old = data["ai"].get("model", "(none)")
    data["ai"]["model"] = model_name
    if "enabled" not in data["ai"]:
        data["ai"]["enabled"] = True

    pattern = re.compile(
        r"(^ai:\s*$[\s\S]*?^\s+model:\s*)(['\"]?)([^'\"\n]+)(\2)",
        re.MULTILINE,
    )
    if pattern.search(text):
        new_text = pattern.sub(
            lambda mo: mo.group(1) + mo.group(2) + model_name + mo.group(4),
            text,
            count=1,
        )
    else:
        new_text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    cfg_file.write_text(new_text, encoding="utf-8")
    print(f"  [ok] AI model changed from '{old}' to '{model_name}'")
    print()
    print("  To pull and start using the model, run:")
    print(f"     ollama pull {model_name}")
    print(f"     ollama run {model_name}")
    print()
    print("  For GPU acceleration, see docs/AI_MODELS.md")
    return True


# ==================================================================
# Refresh AI-visible docs
# ==================================================================
def refresh_ai_docs() -> None:
    @DQ@
    Regenerate the environment manifest so the AI knows about new
    packages and extensions.
    @DQ@
    script = _manifest_script()
    if not script.exists():
        print("  (manifest generator not found)")
        return
    py = _venv_python()
    if not py.exists():
        return
    r = subprocess.run([str(py), str(script)], capture_output=True, text=True)
    if r.returncode == 0:
        print("  [ok] runtime/manifest.md refreshed")


def show_capabilities_tips() -> None:
    @DQ@Print a short note about editing the AI-visible Markdown files.@DQ@
    print()
    print("=" * 60)
    print("  AI-visible Markdown files")
    print("=" * 60)
    print()
    print("  The AI reads these files to understand your environment.")
    print("  Edit them whenever you want to teach the AI something new.")
    print()
    print("  1) Business context (tables, rules, metrics)")
    print(f"     mcp/context/business.md")
    print()
    print("  2) AI capabilities (what it can do, style guide)")
    print(f"     mcp/capabilities.md")
    print()
    print("  3) Environment manifest (auto-generated)")
    print(f"     runtime/manifest.md")
    print("     ^ refreshed automatically when you install packages")
    print()
    print("  Tip: after editing business.md, no restart is needed.")
    print("       The MCP server reads it on every request.")
    print()
    print("  Example: to tell the AI that 'amount' is in Rials, add to")
    print("  business.md:")
    print("     - All monetary columns are in Iranian Rials (IRR).")
    print()
'''
    write(ROOT / "toolkit" / "maintenance.py", content)


# ==================================================================
# 3. docs/OFFLINE_INSTALL.md
# ==================================================================
def write_offline_doc() -> None:
    content = r'''# Installing Packages Offline

This guide shows how to download Python packages and DuckDB extensions
on a machine **with internet**, then install them on a machine
**without internet** (air-gapped server).

---

## Python packages

### Step 1 - on the internet-connected machine

```python
from toolkit.maintenance import download_python_package
download_python_package("statsmodels")
```

This creates `offline/wheels/` with the package and all its
dependencies.

Or from the terminal:

```bash
# Windows
runtime\venv\Scripts\pip.exe download statsmodels -d offline/wheels

# Linux
runtime/venv/bin/pip download statsmodels -d offline/wheels
```

### Step 2 - copy to the offline machine

Copy the entire `offline/wheels/` folder (USB, SCP, etc.) into the
same path on the offline machine:

```
duckdb-portable-toolkit/offline/wheels/
```

### Step 3 - on the offline machine

```python
from toolkit.maintenance import install_python_package_offline
install_python_package_offline("statsmodels")
```

The installer uses `--no-index --find-links=offline/wheels`, so it
never tries to reach the internet.

---

## DuckDB extensions

### Step 1 - on the internet-connected machine

```python
from toolkit.maintenance import download_duckdb_extension
download_duckdb_extension("httpfs")
# For community extensions:
download_duckdb_extension("qvd", community=True)
```

This saves the file to `offline/extensions/httpfs.duckdb_extension`.

### Step 2 - copy to the offline machine

Copy the `.duckdb_extension` file into:

```
duckdb-portable-toolkit/runtime/duckdb/extensions/
```

### Step 3 - on the offline machine

Load it in Python:

```python
import duckdb
con = duckdb.connect()
con.execute("SET extension_directory='runtime/duckdb/extensions'")
con.execute("LOAD httpfs")
```

Or in SQL with the DuckDB CLI:

```bash
runtime/duckdb/duckdb -c "LOAD httpfs;"
```

---

## Things to check

### Python package

- **Python version must match:** both machines should run Python 3.12.
- **Platform must match:** Windows wheels don't work on Linux.

### DuckDB extension

- **DuckDB version must match:** the extension is built for a specific
  DuckDB version.
- **Platform must match:** Windows / Linux / macOS.
- Check with:

  ```python
  import duckdb
  print(duckdb.__version__)
  ```

---

## Refresh the AI-visible manifest

After installing anything, run:

```python
from toolkit.maintenance import refresh_ai_docs
refresh_ai_docs()
```

This regenerates `runtime/manifest.md`, so the AI knows about the new
package or extension.

---

## Where the files live

```
duckdb-portable-toolkit/
├── offline/
│   ├── wheels/                <- .whl files for Python packages
│   └── extensions/            <- .duckdb_extension files
├── runtime/
│   ├── venv/                  <- installed Python packages
│   └── duckdb/
│       └── extensions/        <- installed DuckDB extensions
├── mcp/
│   ├── context/business.md    <- AI business knowledge
│   └── capabilities.md        <- AI capability guide
└── runtime/manifest.md        <- AI-visible manifest (auto-generated)
'''
    write(ROOT / "docs" / "OFFLINE_INSTALL.md", content)


# ==================================================================
# 4. README.md
# ==================================================================
def write_readme() -> None:
    content = r'''# Portable DuckDB Toolkit

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
'''
    write(ROOT / "README.md", content)


# ==================================================================
# Main
# ==================================================================
def main() -> None:
    print("\n=== Applying focused updates ===\n")

    print("1. Fixing banner in setup.py")
    fix_setup_banner()

    print("\n2. Creating toolkit/maintenance.py")
    write_maintenance()

    print("\n3. Creating docs/OFFLINE_INSTALL.md")
    write_offline_doc()

    print("\n4. Rewriting README.md")
    write_readme()

    print("\n" + "=" * 60)
    print("  Done.")
    print("=" * 60)
    print()
    print("  Files updated:")
    print("    - setup.py                (banner only)")
    print("    - README.md               (rewritten)")
    print("    - toolkit/maintenance.py  (new)")
    print("    - docs/OFFLINE_INSTALL.md (new)")
    print()
    print("  Next:")
    print("    git add .")
    print('    git commit -m "update: maintenance module, offline guide"')
    print("    git push")
    print()


if __name__ == "__main__":
    main()