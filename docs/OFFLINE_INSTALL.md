# Installing Packages Offline

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
runtime\python\python.exe -m pip download statsmodels -d offline/wheels

# Linux
runtime/python/bin/python3 -m pip download statsmodels -d offline/wheels
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
duckdb-portable-toolkit/runtime/duckdb/extensions/<version>/<platform>/
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
│   ├── python/                <- portable Python + packages
│   └── duckdb/
│       └── extensions/        <- installed DuckDB extensions
├── mcp/
│   ├── context/business.md    <- AI business knowledge
│   └── capabilities.md        <- AI capability guide
└── runtime/manifest.md        <- AI-visible manifest (auto-generated)