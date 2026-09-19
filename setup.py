#!/usr/bin/env python3
"""
DuckDB Toolkit - Setup

Installs a fully portable Python environment inside the project folder.
No venv, no system modification, no root required.
Works on Windows, Linux, and macOS. Move the folder anywhere.

Profiles:
  1. light     - DuckDB + Jupyter
  2. standard  - + viz + ML + AI + MCP
  3. full      - + EDA + MLflow + all extensions
  4. custom    - like full, but you edit config first
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

if os.name == "nt":
    os.system("")

# ==================================================================
# ANSI colors
# ==================================================================
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_WHITE = "\033[97m"

def _no_color() -> bool:
    return bool(os.environ.get("NO_COLOR")) or not sys.stdout.isatty()

USE_COLOR = not _no_color()

def _c(text: str, *codes: str) -> str:
    if not USE_COLOR:
        return text
    return "".join(codes) + text + C.RESET

def step(title: str) -> None:
    bar = "-" * 64
    print()
    print(_c(bar, C.BRIGHT_CYAN))
    print(_c("  " + title, C.BOLD, C.BRIGHT_CYAN))
    print(_c(bar, C.BRIGHT_CYAN))
    print()

def ok(msg: str) -> None:
    print("  " + _c("OK", C.BOLD, C.BRIGHT_GREEN) + "  " + msg)

def warn(msg: str) -> None:
    print("  " + _c("!!", C.BOLD, C.BRIGHT_YELLOW) + "  " + msg)

def err(msg: str) -> None:
    print("  " + _c("XX", C.BOLD, C.BRIGHT_RED) + "  " + msg)

def info(msg: str) -> None:
    print("  " + _c(msg, C.DIM))

def heading(msg: str) -> None:
    print()
    print(_c("  " + msg, C.BOLD, C.BRIGHT_MAGENTA))
    print()

def key_value(key: str, value: str) -> None:
    print("  " + _c(f"{key:<18}", C.CYAN) + ": " + str(value))

# ==================================================================
# Constants
# ==================================================================
HERE = Path(__file__).parent.resolve()
CONFIG_FILE = HERE / "config.yaml"
PROFILES_DIR = HERE / "configs"

OS = platform.system().lower()
ARCH_RAW = platform.machine().lower()
ARCH = {
    "x86_64": "x86_64",
    "amd64": "x86_64",
    "aarch64": "aarch64",
    "arm64": "aarch64",
}.get(ARCH_RAW, "x86_64")

PY_BUILD_TAG = "20241016"

# ==================================================================
# PyYAML bootstrap
# ==================================================================
def _ensure_yaml() -> Any:
    try:
        import yaml
        return yaml
    except ImportError:
        warn("PyYAML not found. Installing for system Python...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "pyyaml"],
            check=False,
        )
        import yaml
        return yaml

yaml = _ensure_yaml()

# ==================================================================
# Banner
# ==================================================================
def print_banner() -> None:
    print()
    if USE_COLOR:
        banner = r"""
  ____             _         ____  ____
 |  _ \ _   _  ___| | __    |  _ \| __ )
 | | | | | | |/ __| |/ /    | | | |  _ \
 | |_| | |_| | (__|   <     | |_| | |_) |
 |____/ \__,_|\___|_|\_\    |____/|____/

         p o r t a b l e   t o o l k i t
"""
        print(_c(banner, C.BRIGHT_CYAN))
    else:
        print("  DuckDB Toolkit")
        print()
    print(_c("  A fully portable data + ML environment.", C.DIM))
    print(_c("  Windows, Linux, and macOS. No root needed.", C.DIM))
    print()

# ==================================================================
# Profile selection
# ==================================================================
PROFILE_INFO = [
    ("1", "light",    "DuckDB + Jupyter",                     "~700 MB"),
    ("2", "standard", "+ viz + ML + AI + MCP",                "~2.5 GB"),
    ("3", "full",     "+ EDA + MLflow + all extensions",      "~5.7 GB"),
    ("4", "custom",   "Like full, but you edit config first", "varies"),
]

def show_profile_table() -> None:
    heading("Installation Profiles")
    for opt, name, desc, size in PROFILE_INFO:
        line = (
            "    " + _c(opt, C.BOLD, C.BRIGHT_CYAN)
            + "  " + _c(name, C.BRIGHT_MAGENTA).ljust(20)
            + "  " + desc.ljust(42)
            + "  " + _c(size, C.BRIGHT_GREEN)
        )
        print(line)
    print()

def prompt_profile_cli() -> str:
    while True:
        print(_c("  Choose 1, 2, 3, or 4", C.BOLD))
        print("     " + _c("1", C.BRIGHT_CYAN) + " - light")
        print("     " + _c("2", C.BRIGHT_CYAN) + " - standard   " + _c("(recommended)", C.DIM))
        print("     " + _c("3", C.BRIGHT_CYAN) + " - full")
        print("     " + _c("4", C.BRIGHT_CYAN) + " - custom")
        print()
        try:
            choice = input("  > ").strip() or "2"
        except EOFError:
            choice = "2"
        if choice in ("1", "light"):
            return "light"
        if choice in ("2", "standard"):
            return "standard"
        if choice in ("3", "full"):
            return "full"
        if choice in ("4", "custom"):
            return "custom"
        err("Invalid choice: " + repr(choice))

def prompt_existing_config() -> str:
    heading("config.yaml already exists")
    key_value("File", str(CONFIG_FILE))
    try:
        key_value("Size", str(CONFIG_FILE.stat().st_size) + " bytes")
    except Exception:
        pass
    print()
    print(_c("  What would you like to do?", C.BOLD))
    print("     " + _c("K", C.BRIGHT_CYAN) + " - keep the existing config and install")
    print("     " + _c("O", C.BRIGHT_CYAN) + " - overwrite it (choose a new profile)")
    print("     " + _c("E", C.BRIGHT_CYAN) + " - exit so you can edit it")
    print()
    while True:
        try:
            choice = input("  > ").strip().upper() or "K"
        except EOFError:
            choice = "K"
        if choice in ("K", "KEEP"):
            return "keep"
        if choice in ("O", "OVERWRITE"):
            return "overwrite"
        if choice in ("E", "EDIT"):
            return "edit"
        err("Invalid choice: " + repr(choice))

def choose_profile(force: str | None = None) -> str:
    if force:
        if force not in ("light", "standard", "full", "custom"):
            err("Unknown profile: " + force)
            sys.exit(1)
        ok("Using profile from CLI: " + force)
        return force

    if CONFIG_FILE.exists():
        decision = prompt_existing_config()
        if decision == "keep":
            return "keep"
        if decision == "edit":
            print()
            info("Edit config.yaml and run setup.py again.")
            sys.exit(0)

    show_profile_table()
    return prompt_profile_cli()

def apply_profile(profile: str) -> None:
    if profile == "keep":
        ok("Using existing config.yaml")
        return
    src = PROFILES_DIR / ("config." + profile + ".yaml")
    if not src.exists():
        err("Profile config not found: " + str(src))
        sys.exit(1)
    shutil.copy2(src, CONFIG_FILE)
    ok("Profile '" + profile + "' written to config.yaml")

    if profile == "custom":
        print()
        heading("Custom profile - edit your config")
        print(_c("  Next steps:", C.BOLD))
        print("     1. Open " + _c(str(CONFIG_FILE), C.BRIGHT_CYAN))
        print("     2. Edit paths, packages, AI model, etc.")
        print("     3. Run " + _c("python setup.py", C.BRIGHT_GREEN) + " again")
        print()
        sys.exit(0)

# ==================================================================
# Config loading
# ==================================================================
def load_config() -> dict:
    if not CONFIG_FILE.exists():
        err("config.yaml not found")
        sys.exit(1)
    with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)

def resolve(base: Path, value: str) -> Path:
    p = Path(value).expanduser()
    return p if p.is_absolute() else (base / p).resolve()

class Paths:
    def __init__(self, cfg: dict) -> None:
        base = Path(cfg["paths"]["project_root"]).expanduser()
        if not base.is_absolute():
            base = (HERE / base).resolve()
        self.project_root = base
        p = cfg["paths"]
        self.runtime_dir    = resolve(base, p["runtime_dir"])
        self.python_dir     = resolve(base, p["python_dir"])
        self.duckdb_dir     = resolve(base, p["duckdb_dir"])
        self.extensions_dir = resolve(base, p["extensions_dir"])
        self.models_dir     = resolve(base, p["models_dir"])
        self.jobs_dir       = resolve(base, p.get("jobs_dir", "jobs"))
        self.configs_dir    = resolve(base, p.get("configs_dir", "configs"))
        self.data_dir       = resolve(base, p.get("data_dir", "data"))
        self.exports_dir    = resolve(base, p.get("exports_dir", "exports"))
        self.logs_dir       = resolve(base, p.get("logs_dir", "logs"))
        self.mlruns_dir     = resolve(base, p.get("mlruns_dir", "mlruns"))
        self.reports_dir    = resolve(base, p.get("reports_dir", "reports"))

# ==================================================================
# Executable paths
# ==================================================================
def python_exe(paths: Paths) -> Path:
    return (paths.python_dir / "python.exe" if OS == "windows"
            else paths.python_dir / "bin" / "python3")

def site_packages(paths: Paths) -> Path:
    py = python_exe(paths)
    if not py.exists():
        return Path()
    r = subprocess.run(
        [str(py), "-c",
         "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return Path()
    return Path(r.stdout.strip())

# ==================================================================
# Download helpers
# ==================================================================
def download(url: str, dest: Path, retries: int = 3) -> None:
    info("downloading " + url)
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, retries + 1):
        try:
            urllib.request.urlretrieve(url, dest)
            size_mb = dest.stat().st_size / 1024 / 1024
            ok("saved " + dest.name + "  (" + format(size_mb, ".1f") + " MB)")
            return
        except Exception as exc:
            if attempt < retries:
                warn("attempt " + str(attempt) + " failed: " + str(exc) + ". retrying...")
                time.sleep(2 * attempt)
            else:
                err("download failed after " + str(retries) + " attempts: " + str(exc))
                raise

def extract_tar_gz(archive: Path, target: Path) -> None:
    with tarfile.open(archive, "r:gz") as t:
        t.extractall(target)
    archive.unlink()

def extract_zip(archive: Path, target: Path) -> None:
    with zipfile.ZipFile(archive) as z:
        z.extractall(target)
    archive.unlink()

def make_executable(path: Path) -> None:
    if OS != "windows" and path.exists():
        os.chmod(path, 0o755)

# ==================================================================
# 1. Create directory structure
# ==================================================================
def create_dirs(paths: Paths) -> None:
    step("Creating directory structure")
    for d in [paths.runtime_dir, paths.duckdb_dir, paths.extensions_dir,
              paths.models_dir, paths.jobs_dir, paths.configs_dir,
              paths.data_dir, paths.exports_dir, paths.logs_dir,
              paths.mlruns_dir, paths.reports_dir]:
        d.mkdir(parents=True, exist_ok=True)
        try:
            rel = d.relative_to(paths.project_root)
            ok(str(rel))
        except ValueError:
            ok(str(d))

# ==================================================================
# 2. Portable Python
# ==================================================================
def platform_tag() -> str:
    if OS == "windows":
        return "x86_64-pc-windows-msvc" if ARCH == "x86_64" else "aarch64-pc-windows-msvc"
    if OS == "darwin":
        return "x86_64-apple-darwin" if ARCH == "x86_64" else "aarch64-apple-darwin"
    return ARCH + "-unknown-linux-gnu"

def python_build_url(version: str) -> tuple[str, str]:
    base = ("https://github.com/astral-sh/python-build-standalone/"
            "releases/download/" + PY_BUILD_TAG)
    filename = ("cpython-" + version + "+" + PY_BUILD_TAG + "-"
                + platform_tag() + "-install_only.tar.gz")
    return base + "/" + filename, filename

def install_portable_python(paths: Paths, cfg: dict) -> None:
    step("Installing portable Python " + cfg["python"]["version"])

    if not cfg["setup"].get("download_python", True):
        warn("skipped by config")
        return

    py = python_exe(paths)
    if py.exists() and cfg["setup"].get("skip_existing", True):
        r = subprocess.run([str(py), "--version"],
                           capture_output=True, text=True)
        ok("already present: " + (r.stdout.strip() or r.stderr.strip()))
        return

    version = cfg["python"]["version"]
    url, archive_name = python_build_url(version)
    archive = paths.runtime_dir / archive_name
    download(url, archive)

    tmp = paths.runtime_dir / "_tmp_python"
    if tmp.exists():
        shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True, exist_ok=True)
    extract_tar_gz(archive, tmp)

    src = tmp / "python"
    if paths.python_dir.exists():
        shutil.rmtree(paths.python_dir, ignore_errors=True)
    if src.exists():
        shutil.move(str(src), str(paths.python_dir))
    else:
        shutil.move(str(tmp), str(paths.python_dir))
    shutil.rmtree(tmp, ignore_errors=True)
    make_executable(py)

    if OS != "windows":
        bin_dir = paths.python_dir / "bin"
        if bin_dir.exists():
            for f in bin_dir.glob("*"):
                if f.is_file():
                    os.chmod(f, 0o755)

    r = subprocess.run([str(py), "--version"],
                       capture_output=True, text=True)
    ok("Python installed: " + (r.stdout.strip() or r.stderr.strip()))

# ==================================================================
# 3. Package groups
# ==================================================================
PKG_GROUPS = {
    "core": [
        "duckdb", "pandas", "pyarrow", "numpy", "polars",
    ],
    "jupyter": [
        "jupyterlab", "jupysql", "duckdb-engine", "sqlalchemy",
        "ipywidgets", "ipykernel",
        "jupyter-ai", "jupyter-ai-jupyternaut", "fastmcp",
    ],
    "visualization": [
        "matplotlib", "seaborn", "plotly", "altair", "bokeh",
        "holoviews", "kaleido",
    ],
    "streamlit": [
        "streamlit", "streamlit-aggrid",
    ],
    "eda": [
        "missingno", "ydata-profiling", "sweetviz",
        "autoviz", "dtale", "lazypredict", "sklearn-pandas",
    ],
    "data_quality": [
        "great-expectations", "pandera",
    ],
    "notebook_tools": [
        "papermill", "nbformat", "nbconvert", "jupyterlab-git",
    ],
    "scheduling": [
        "schedule", "apscheduler",
    ],
    "ml": [
        "scikit-learn", "xgboost", "lightgbm",
        "transformers", "datasets", "sentence-transformers",
    ],
    "mlops": [
        "mlflow", "optuna",
    ],
    "cloud": [
        "boto3", "openpyxl", "qvdrs[duckdb]",
    ],
    "connectors": [
        "kafka-python",          # lightweight Kafka client
        "confluent-kafka",       # faster Kafka client (librdkafka)
        "trino",                 # Trino DBAPI client
         # Flink SQL Gateway DBAPI client
    ],
    "utilities": [
        "pyyaml", "requests", "tqdm", "loguru", "rich",
        "humanize", "tabulate", "jinja2", "markdown", "pydantic",
        "mcp", "openai-whisper", "certifi",
        "openai",
        "litellm",
    ],
}

def pip_install(py: str, package: str, retries: int = 3) -> bool:
    for attempt in range(1, retries + 1):
        r = subprocess.run(
            [py, "-m", "pip", "install", package,
             "--no-warn-script-location",
             "--disable-pip-version-check",
             "--timeout", "120"],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            return True
        if attempt < retries:
            warn("retry " + str(attempt) + "/" + str(retries) + " for " + package)
            time.sleep(3 * attempt)
    return False

def install_packages(paths: Paths, cfg: dict) -> None:
    step("Installing Python packages (directly, no venv)")

    if not cfg["setup"].get("install_packages", True):
        warn("skipped by config")
        return

    py = str(python_exe(paths))

    subprocess.run(
        [py, "-m", "pip", "install", "--upgrade",
         "pip", "setuptools", "wheel",
         "--no-warn-script-location",
         "--disable-pip-version-check"],
        check=True,
    )
    ok("pip, setuptools, wheel upgraded")

    enabled = cfg.get("packages", {})
    failed = []

    for group, pkgs in PKG_GROUPS.items():
        if not enabled.get(group, True):
            info("skipping group: " + group)
            continue
        heading("group: " + group)
        for pkg in pkgs:
            info("installing " + pkg + " ...")
            if pip_install(py, pkg):
                ok(pkg)
            else:
                err(pkg + " failed")
                failed.append(pkg)

    if enabled.get("ml", True):
        heading("PyTorch")
        build = cfg.get("pytorch", {}).get("build", "cpu").lower()
        cuda = cfg.get("pytorch", {}).get("cuda_version", "cu121")
        index = ("https://download.pytorch.org/whl/" + cuda if build == "cuda"
                 else "https://download.pytorch.org/whl/cpu")
        r = subprocess.run(
            [py, "-m", "pip", "install", "torch", "torchvision",
             "--index-url", index,
             "--no-warn-script-location",
             "--disable-pip-version-check",
             "--timeout", "120"],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            ok("torch + torchvision (" + build + ")")
        else:
            err("torch install failed")
            failed.extend(["torch", "torchvision"])

    if failed:
        heading("Packages that failed")
        for p in failed:
            err(p)
        print()
        info("retry with: " + py + " -m pip install " + " ".join(failed))
    else:
        ok("all packages installed")

# ==================================================================
# 4. DuckDB CLI
# ==================================================================
def install_duckdb(paths: Paths, cfg: dict) -> None:
    step("Installing DuckDB CLI")

    if not cfg["setup"].get("download_duckdb", True):
        warn("skipped by config")
        return

    exe_name = "duckdb.exe" if OS == "windows" else "duckdb"
    exe_path = paths.duckdb_dir / exe_name

    if exe_path.exists() and cfg["setup"].get("skip_existing", True):
        ok("already present: " + exe_path.name)
        return

    plat = {
        ("windows", "x86_64"): "windows-amd64",
        ("linux", "x86_64"):   "linux-amd64",
        ("linux", "aarch64"):  "linux-arm64",
        ("darwin", "x86_64"):  "osx-amd64",
        ("darwin", "aarch64"): "osx-arm64",
    }.get((OS, ARCH), "linux-amd64")

    url = ("https://github.com/duckdb/duckdb/releases/latest/download/"
           "duckdb_cli-" + plat + ".zip")
    archive = paths.duckdb_dir / "duckdb.zip"
    download(url, archive)
    extract_zip(archive, paths.duckdb_dir)
    make_executable(exe_path)
    ok("DuckDB CLI ready")

# ==================================================================
# 5. DuckDB extensions
# ==================================================================
def install_extensions(paths: Paths, cfg: dict) -> None:
    step("Installing DuckDB extensions")

    if not cfg["setup"].get("install_extensions", True):
        warn("skipped by config")
        return

    exe = paths.duckdb_dir / ("duckdb.exe" if OS == "windows" else "duckdb")
    if not exe.exists():
        warn("DuckDB CLI not found, skipping extensions")
        return

    ext = cfg.get("extensions", {})
    todo = ([(n, "core") for n in ext.get("core", [])] +
            [(n, "community") for n in ext.get("community", [])])

    for name, repo in todo:
        src = "FROM community" if repo == "community" else ""
        sql = ("SET extension_directory='" + str(paths.extensions_dir) + "'; "
               "INSTALL " + name + " " + src + ";")
        r = subprocess.run([str(exe), "-c", sql],
                           capture_output=True, text=True)
        if r.returncode == 0:
            ok(name + "  (" + repo + ")")
        else:
            if name in ("whisper", "cassandra") and OS == "windows":
                info(f"{name} ({repo}) - not available for Windows (this is fine)")
                if name == "whisper":
                    info("  Use the openai-whisper Python package instead")
                elif name == "cassandra":
                    info("  Use ODBC or a Python Cassandra driver")
            else:
                warn(name + "  (" + repo + ") - skipped")
    ok("extensions processed")

# ==================================================================
# 6. llama.cpp
# ==================================================================
def install_llama_cpp(paths: Paths, cfg: dict) -> None:
    step("Setting up llama.cpp")

    ai = cfg.get("ai", {})
    if not ai.get("enabled", False):
        warn("AI assistant disabled in config")
        return
    if ai.get("provider") != "llama.cpp":
        warn("AI provider is not llama.cpp")
        return

    bin_dir = paths.project_root / ai["bin_dir"]
    exe_name = "llama-server.exe" if OS == "windows" else "llama-server"
    server_exe = bin_dir / exe_name

    if server_exe.exists() and cfg["setup"].get("skip_existing", True):
        ok("already present: " + server_exe.name)
        return

    bin_dir.mkdir(parents=True, exist_ok=True)

    urls = {
        ("windows", "x86_64"): ai["download_urls"]["windows"],
        ("linux", "x86_64"):   ai["download_urls"]["linux"],
        ("darwin", "x86_64"):  ai["download_urls"].get("macos", ""),
        ("darwin", "aarch64"): ai["download_urls"].get("macos_arm", ""),
    }
    url = urls.get((OS, ARCH), ai["download_urls"]["linux"])

    if not url:
        warn("no llama.cpp URL for " + OS + "/" + ARCH)
        return

    archive = bin_dir / "llama.cpp.zip"
    download(url, archive)
    extract_zip(archive, bin_dir)

    if OS != "windows":
        for f in bin_dir.rglob("*"):
            if f.is_file():
                os.chmod(f, 0o755)

    if server_exe.exists():
        ok("llama.cpp installed")
        return

    for candidate in bin_dir.rglob(exe_name):
        shutil.move(str(candidate), str(server_exe))
        make_executable(server_exe)
        ok("llama.cpp installed (moved from subfolder)")
        return

    err(exe_name + " not found after extraction")

# ==================================================================
# 7. AI model (GGUF)
# ==================================================================
# ==================================================================
# BI drivers (ODBC + JDBC for DuckDB)
# ==================================================================
def install_bi_drivers(paths: Paths, cfg: dict) -> None:
    """Download ODBC and JDBC drivers for DuckDB into runtime/duckdb/drivers/."""
    step("Installing BI drivers (ODBC + JDBC)")

    bi_cfg = cfg.get("bi_drivers", {})
    if not bi_cfg.get("enabled", True):
        warn("BI drivers disabled in config")
        return

    drivers_dir = paths.duckdb_dir / "drivers"
    drivers_dir.mkdir(parents=True, exist_ok=True)

    # ---------- JDBC ----------
    jdbc_target = drivers_dir / "duckdb_jdbc.jar"
    if jdbc_target.exists() and cfg["setup"].get("skip_existing", True):
        size_mb = jdbc_target.stat().st_size / 1024 / 1024
        ok(f"JDBC already present: {jdbc_target.name} ({size_mb:.1f} MB)")
    else:
        jdbc_url = (
            "https://repo1.maven.org/maven2/org/duckdb/"
            "duckdb_jdbc/1.3.1.0/duckdb_jdbc-1.3.1.0.jar"
        )
        try:
            download(jdbc_url, jdbc_target)
            size_mb = jdbc_target.stat().st_size / 1024 / 1024
            ok(f"JDBC driver: {jdbc_target.name} ({size_mb:.1f} MB)")
        except Exception as exc:
            warn(f"JDBC download failed: {exc}")

    # ---------- ODBC (Windows only) ----------
    if OS == "windows":
        odbc_zip = drivers_dir / "duckdb_odbc.zip"
        if odbc_zip.exists() and cfg["setup"].get("skip_existing", True):
            ok(f"ODBC archive already present: {odbc_zip.name}")
        else:
            odbc_url = (
                "https://github.com/duckdb/duckdb-odbc/releases/"
                "latest/download/duckdb_odbc-windows-amd64.zip"
            )
            try:
                download(odbc_url, odbc_zip)
                # Extract the archive
                extract_zip(odbc_zip, drivers_dir)
                ok(f"ODBC driver extracted to runtime/duckdb/drivers/")
            except Exception as exc:
                warn(f"ODBC download failed: {exc}")
                info("You can install it manually later.")
    else:
        info("ODBC on Linux/macOS: install via package manager or build from source")

    # ---------- README ----------
    readme = drivers_dir / "README.md"
    readme.write_text(DRIVERS_README, encoding="utf-8")
    ok("Created drivers/README.md")

DRIVERS_README = """# DuckDB BI Drivers

This folder contains ODBC and JDBC drivers for DuckDB, so BI tools
like Tableau, Power BI, and Qlik Sense can connect directly.

## Files

- `duckdb_jdbc.jar` - JDBC driver (for Tableau, Qlik, etc.)
- `duckdb_odbc.dll` (Windows) - ODBC driver
- `odbc_install.exe` (Windows) - ODBC installer

## Tableau (JDBC)

1. Copy `duckdb_jdbc.jar` to:
   - Windows: `C:\\Program Files\\Tableau\\<version>\\Drivers\\`
   - macOS: `~/Library/Tableau/Drivers/`
2. Restart Tableau
3. Connect using "Other Databases (JDBC)"
4. URL format: `jdbc:duckdb:/path/to/database.duckdb`

## Power BI (ODBC)

1. Run `odbc_install.exe` as Administrator
2. Open "ODBC Data Sources (64-bit)"
3. Add a new System DSN of type "DuckDB Driver"
4. Point it to your `.duckdb` file
5. In Power BI: Get Data -> ODBC -> select the DSN

## Qlik Sense (ODBC)

1. Run `odbc_install.exe` as Administrator
2. In Qlik Sense: Create new connection -> ODBC
3. Select the DuckDB DSN
4. Use the connection in the Data Load Editor

## Notes

- All BI tools connect read-only to DuckDB
- The database file must not be locked by another process
- For live dashboards, export data to Parquet and connect the BI
  tool to Parquet instead (faster)
"""

def install_ai_model(paths: Paths, cfg: dict) -> None:
    step("Setting up AI model")

    ai = cfg.get("ai", {})
    if not ai.get("enabled", False):
        warn("AI assistant disabled")
        return
    if ai.get("provider") != "llama.cpp":
        warn("AI provider is not llama.cpp")
        return

    m = ai["model"]
    model_dir = paths.project_root / m["dir"]
    model_path = model_dir / m["filename"]

    if model_path.exists() and cfg["setup"].get("skip_existing", True):
        size_gb = model_path.stat().st_size / (1024 ** 3)
        ok("already present: " + m["filename"] + " (" + format(size_gb, ".2f") + " GB)")
        return

    model_dir.mkdir(parents=True, exist_ok=True)
    info("downloading " + m["filename"] + " (~" + str(m.get("size_gb", 1)) + " GB) ...")
    download(m["download_url"], model_path)

# ==================================================================
# 8. tiktoken cache
# ==================================================================
TIKTOKEN_URL = ("https://openaipublic.blob.core.windows.net/"
                "encodings/cl100k_base.tiktoken")

def install_tiktoken_cache(paths: Paths, cfg: dict) -> None:
    step("Caching tiktoken encodings")

    py = str(python_exe(paths))

    # Ensure certifi
    r = subprocess.run([py, "-c", "import certifi; print(certifi.where())"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        info("installing certifi ...")
        subprocess.run(
            [py, "-m", "pip", "install", "certifi",
             "--no-warn-script-location",
             "--disable-pip-version-check"],
            capture_output=True, text=True,
        )
        r = subprocess.run([py, "-c", "import certifi; print(certifi.where())"],
                           capture_output=True, text=True)

    if r.returncode == 0:
        cert = r.stdout.strip()
        os.environ["SSL_CERT_FILE"] = cert
        os.environ["REQUESTS_CA_BUNDLE"] = cert

    cache_dir = paths.runtime_dir / "tiktoken_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    target = cache_dir / "cl100k_base.tiktoken"
    if target.exists():
        ok("cl100k_base.tiktoken already cached")
    else:
        try:
            info("downloading cl100k_base.tiktoken ...")
            urllib.request.urlretrieve(TIKTOKEN_URL, str(target))
            ok("saved cl100k_base.tiktoken")
        except Exception as exc:
            warn("could not download: " + str(exc))
            info("This is only needed if you use Jupyter AI offline.")

    env_file = paths.project_root / ".env"
    line = "TIKTOKEN_CACHE_DIR=" + cache_dir.as_posix()
    if env_file.exists():
        content = env_file.read_text(encoding="utf-8")
        if "TIKTOKEN_CACHE_DIR" not in content:
            env_file.write_text(content.rstrip() + "\n" + line + "\n",
                                encoding="utf-8")
    else:
        env_file.write_text(line + "\n", encoding="utf-8")

# ==================================================================
# 9. Patch launchers
# ==================================================================
def patch_launchers(paths: Paths) -> None:
    step("Patching launchers")

    bat = paths.project_root / "start-jupyter.bat"
    if bat.exists():
        text = bat.read_text(encoding="utf-8")
        if "TIKTOKEN_CACHE_DIR" not in text:
            marker = 'cd /d "%~dp0"\r\n'
            marker_lf = 'cd /d "%~dp0"\n'
            nl = "\r\n" if marker in text else "\n"
            used_marker = marker if marker in text else marker_lf
            insert = (
                used_marker
                + nl
                + "REM Cache tiktoken files locally" + nl
                + 'set "TIKTOKEN_CACHE_DIR=%~dp0runtime\\tiktoken_cache"' + nl
            )
            if used_marker in text:
                text = text.replace(used_marker, insert, 1)
                bat.write_text(text, encoding="utf-8")
                ok("patched start-jupyter.bat")

    sh = paths.project_root / "start-jupyter.sh"
    if sh.exists():
        text = sh.read_text(encoding="utf-8")
        if "TIKTOKEN_CACHE_DIR" not in text:
            marker = 'cd "$SCRIPT_DIR"\n'
            insert = (
                marker
                + "\n"
                + "# Cache tiktoken files locally\n"
                + 'export TIKTOKEN_CACHE_DIR="$SCRIPT_DIR/runtime/tiktoken_cache"\n'
            )
            if marker in text:
                text = text.replace(marker, insert, 1)
                sh.write_text(text, encoding="utf-8")
                ok("patched start-jupyter.sh")

# ==================================================================
# 10. Jupyter config + silence warnings
# ==================================================================
JUPYTER_CONFIG = """# Auto-generated by setup.py - silence common warnings

c.ServerApp.websocket_ping_interval = 30000
c.ServerApp.websocket_ping_timeout = 30000
c.ServerApp.open_browser = True
c.ServerApp.allow_remote_access = True
c.ServerApp.log_level = "WARN"
"""

def write_jupyter_config(paths: Paths, cfg: dict) -> None:
    step("Writing Jupyter configuration")

    cfg_dir = paths.runtime_dir / "jupyter_config"
    cfg_dir.mkdir(parents=True, exist_ok=True)

    cfg_file = cfg_dir / "jupyter_server_config.py"
    cfg_file.write_text(JUPYTER_CONFIG, encoding="utf-8")
    ok("created runtime/jupyter_config/jupyter_server_config.py")

def suppress_litellm_warning(paths: Paths, cfg: dict) -> None:
    step("Suppressing litellm warning")

    sp = site_packages(paths)
    if not sp or not sp.exists():
        warn("site-packages not found")
        return

    lines = [
        "import warnings",
        "warnings.filterwarnings('ignore', "
        "message=\"Importing 'jupyter_ai_litellm'\")",
    ]
    pth = sp / "duckdb_toolkit_warnings.pth"
    pth.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ok("created duckdb_toolkit_warnings.pth")

def silence_extension_warnings(paths: Paths, cfg: dict) -> None:
    step("Silencing JupyterLab warnings")

    py = str(python_exe(paths))

    # Disable jupyter_server_mcp (we have our own MCP at mcp/server.py)
    subprocess.run(
        [py, "-m", "jupyter", "server", "extension", "disable",
         "jupyter_server_mcp"],
        capture_output=True, text=True,
    )
    ok("jupyter_server_mcp disabled")

    # Remove jupyterlab-plotly (needs a Node.js build step)
    subprocess.run(
        [py, "-m", "pip", "uninstall", "-y", "jupyterlab-plotly"],
        capture_output=True, text=True,
    )
    ok("jupyterlab-plotly removed")

def clean_notebooks(paths: Paths, cfg: dict) -> None:
    step("Cleaning stale notebooks")

    removed = 0
    cleaned = 0

    for nb in paths.project_root.glob("Untitled*.ipynb"):
        try:
            nb.unlink()
            removed += 1
            info("removed " + nb.name)
        except Exception:
            pass

    for nb in paths.project_root.rglob("*.ipynb"):
        if ".ipynb_checkpoints" in str(nb):
            continue
        try:
            data = json.loads(nb.read_text(encoding="utf-8"))
        except Exception:
            continue
        meta = data.get("metadata", {})
        if "kernelspec" in meta:
            name = meta["kernelspec"].get("name", "")
            if name not in ("duckdb-toolkit", "python3"):
                meta.pop("kernelspec", None)
                meta.pop("language_info", None)
                nb.write_text(
                    json.dumps(data, indent=1, ensure_ascii=False),
                    encoding="utf-8",
                )
                cleaned += 1

    if removed:
        ok("removed " + str(removed) + " temporary notebook(s)")
    if cleaned:
        ok("cleaned " + str(cleaned) + " notebook(s)")
    if not removed and not cleaned:
        ok("no stale notebooks found")

def finalize_jupyter_setup(paths: Paths, cfg: dict) -> None:
    """Run all warning-silencing steps at the end of setup."""
    write_jupyter_config(paths, cfg)
    suppress_litellm_warning(paths, cfg)
    silence_extension_warnings(paths, cfg)
    clean_notebooks(paths, cfg)

# ==================================================================
# 11. Whisper model
# ==================================================================
def install_whisper_model(paths: Paths, cfg: dict) -> None:
    step("Downloading Whisper model")

    whisper_cfg = cfg.get("whisper", {})
    if not whisper_cfg.get("enabled", True):
        warn("Whisper disabled in config")
        return

    model = whisper_cfg.get("model", "small")
    size_gb = {"tiny": 0.075, "base": 0.142, "small": 0.466,
               "medium": 1.5, "large": 3.0}.get(model, 0.466)

    home = Path.home()
    cache = home / ".cache" / "whisper"

    if cache.exists() and any(cache.glob(model + "*")):
        ok("Whisper '" + model + "' model already cached")
        return

    cache.mkdir(parents=True, exist_ok=True)

    py = str(python_exe(paths))
    info("downloading Whisper '" + model + "' model (~"
         + format(size_gb, ".2f") + " GB) ...")
    info("(this happens only once and is cached for offline use)")

    code = (
        "import whisper;"
        "whisper.load_model('" + model + "');"
        "print('ok')"
    )
    r = subprocess.run([py, "-c", code],
                       capture_output=True, text=True, timeout=900)
    if r.returncode == 0:
        ok("Whisper '" + model + "' downloaded to " + str(cache))
    else:
        warn("Whisper model download failed")
        if r.stderr:
            print("       " + r.stderr.strip().splitlines()[-1][:200])

# ==================================================================
# 12. Register toolkit import (.pth)
# ==================================================================
def register_toolkit_import(paths: Paths) -> None:
    step("Registering toolkit import path")

    sp = site_packages(paths)
    if not sp or not sp.exists():
        warn("site-packages not found")
        return

    try:
        rel = os.path.relpath(paths.project_root, sp).replace("\\", "/")
    except ValueError:
        rel = str(paths.project_root).replace("\\", "/")

    pth = sp / "duckdb_toolkit.pth"
    pth.write_text(rel + "\n", encoding="utf-8")
    ok("created " + pth.name)
    info("relative path: " + rel)

# ==================================================================
# 13. Register Jupyter kernel
# ==================================================================
def register_kernel(paths: Paths) -> None:
    step("Registering Jupyter kernel")

    py = python_exe(paths)
    if not py.exists():
        warn("Python not installed")
        return

    r = subprocess.run([str(py), "-c", "import ipykernel"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        info("ipykernel not found, installing ...")
        subprocess.run(
            [str(py), "-m", "pip", "install", "ipykernel",
             "--no-warn-script-location",
             "--disable-pip-version-check"],
            check=False,
        )

    r = subprocess.run(
        [str(py), "-m", "ipykernel", "install", "--user",
         "--name", "duckdb-toolkit",
         "--display-name", "DuckDB Toolkit (portable)"],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        ok("kernel 'DuckDB Toolkit (portable)' registered")
    else:
        warn("kernel registration failed")

# ==================================================================
# 14. Manifest
# ==================================================================
def generate_manifest(paths: Paths) -> None:
    step("Generating environment manifest")
    script = paths.project_root / "mcp" / "manifest_generator.py"
    if not script.exists():
        warn("manifest_generator.py not found")
        return
    py = str(python_exe(paths))
    r = subprocess.run([py, str(script)], capture_output=True, text=True)
    if r.returncode == 0:
        ok("runtime/manifest.md generated")
    else:
        warn("manifest generation failed")

# ==================================================================
# 15. Config files
# ==================================================================
SECRETS_TEMPLATE = """-- Database secrets - fill in your credentials.
CREATE SECRET IF NOT EXISTS ora (
    TYPE oracle, HOST 'oracle-host', PORT 1521,
    SERVICE_NAME 'ORCLPDB1', USER 'user', PASSWORD 'pass'
);
CREATE SECRET IF NOT EXISTS pg (
    TYPE postgres, HOST 'pg-host', PORT 5432,
    DATABASE 'mydb', USER 'user', PASSWORD 'pass'
);
CREATE SECRET IF NOT EXISTS mysql (
    TYPE mysql, HOST 'mysql-host', PORT 3306,
    DATABASE 'mydb', USER 'user', PASSWORD 'pass'
);
"""

def write_configs(paths: Paths, cfg: dict) -> None:
    step("Writing configuration files")
    if not cfg["setup"].get("create_config_files", True):
        warn("skipped by config")
        return

    secrets = paths.configs_dir / "secrets.sql"
    if not secrets.exists():
        secrets.write_text(SECRETS_TEMPLATE, encoding="utf-8")
        ok("created configs/secrets.sql")
    else:
        ok("kept existing configs/secrets.sql")

    paths_json = paths.configs_dir / "paths.json"
    try:
        rel_paths = {}
        for k, v in vars(paths).items():
            vp = Path(v)
            if vp.is_absolute() and str(vp).startswith(str(paths.project_root)):
                rel_paths[k] = str(vp.relative_to(paths.project_root)).replace("\\", "/")
            else:
                rel_paths[k] = str(v)
    except Exception:
        rel_paths = {k: str(v) for k, v in vars(paths).items()}
    paths_json.write_text(
        json.dumps(rel_paths, indent=2),
        encoding="utf-8",
    )
    ok("created configs/paths.json (relative paths)")

# ==================================================================
# Main
# ==================================================================
def main() -> None:
    parser = argparse.ArgumentParser(description="DuckDB Toolkit Setup")
    parser.add_argument("--profile", "-p",
                        choices=["light", "standard", "full", "custom"],
                        help="Skip the prompt and use this profile")
    args = parser.parse_args()

    print_banner()

    profile = choose_profile(force=args.profile)
    apply_profile(profile)

    cfg = load_config()
    paths = Paths(cfg)

    step("Configuration")
    key_value("OS", OS)
    key_value("Architecture", ARCH)
    key_value("Python version", cfg["python"]["version"])
    key_value("Project root", str(paths.project_root))
    key_value("Runtime dir", str(paths.runtime_dir))
    key_value("PyTorch build", cfg.get("pytorch", {}).get("build", "cpu"))
    key_value("AI provider", cfg.get("ai", {}).get("provider", "(none)"))
    _ai = cfg.get("ai", {}) or {}
    _model = _ai.get("model", {})
    if isinstance(_model, dict):
        _model = _model.get("filename", "(none)")
    key_value("AI model", str(_model))
    key_value("MCP server", str(cfg.get("mcp", {}).get("enabled", False)))

    create_dirs(paths)
    install_portable_python(paths, cfg)
    install_packages(paths, cfg)
    install_duckdb(paths, cfg)
    install_extensions(paths, cfg)
    install_bi_drivers(paths, cfg)
    install_llama_cpp(paths, cfg)
    install_ai_model(paths, cfg)
    install_tiktoken_cache(paths, cfg)
    patch_launchers(paths)
    finalize_jupyter_setup(paths, cfg)
    install_whisper_model(paths, cfg)
    register_toolkit_import(paths)
    register_kernel(paths)
    generate_manifest(paths)
    write_configs(paths, cfg)

    print()
    bar = "=" * 64
    print(_c(bar, C.BOLD, C.BRIGHT_GREEN))
    print(_c("  Setup complete!", C.BOLD, C.BRIGHT_GREEN))
    print(_c(bar, C.BOLD, C.BRIGHT_GREEN))
    print()

    heading("Optional connectors")
    info("Kafka, Trino, and Flink SQL Gateway clients are installed")
    info("in the connectors group. For Flink SQL Gateway, start the")
    info("gateway on your cluster and point the client to it.")
    info("")
    info("Java (JRE) 11 or 17 is recommended for full Spark support.")
    info("")

    heading("Next steps")
    if OS == "windows":
        launch = "start-jupyter.bat"
    else:
        launch = "./start-jupyter.sh"

    print("  " + _c("1.", C.BOLD) + " Launch JupyterLab:")
    print("     " + _c(launch, C.BRIGHT_CYAN))
    print()
    print("  " + _c("2.", C.BOLD) + " In JupyterLab, select the kernel:")
    print("     " + _c("DuckDB Toolkit (portable)", C.BRIGHT_CYAN))
    print()
    print("  " + _c("3.", C.BOLD) + " Edit your business context for the AI:")
    print("     " + _c("mcp/context/business.md", C.BRIGHT_CYAN))
    print()
    print("  " + _c("4.", C.BOLD) + " Edit database credentials:")
    print("     " + _c("configs/secrets.sql", C.BRIGHT_CYAN))
    print()
    print("  " + _c("5.", C.BOLD) + " Verify installation:")
    if OS == "windows":
        cmd = "runtime\\python\\python.exe verify.py"
    else:
        cmd = "runtime/python/bin/python3 verify.py"
    print("     " + _c(cmd, C.BRIGHT_GREEN))
    print()

if __name__ == "__main__":
    main()