#!/usr/bin/env python3
"""
Portable DuckDB Toolkit - Setup.

Four installation profiles:
  1. light     - DuckDB + Jupyter (minimal)
  2. standard  - + viz + basic ML + AI + MCP
  3. full      - + everything (EDA, MLflow, all extensions)
  4. custom    - like full, but you edit config first

Uses python-build-standalone, creates an isolated venv, installs packages
into the project folder, and downloads DuckDB + extensions.

Works on Windows and Linux. Fully portable.
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


# ==================================================================
# Enable ANSI colors on Windows terminals
# ==================================================================
if os.name == "nt":
    os.system("")  # enables VT100 processing on Windows 10+


# ==================================================================
# ANSI color helpers (no external dependencies)
# ==================================================================
class C:
    """ANSI color codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


def _no_color() -> bool:
    """Disable colors when NO_COLOR is set or output is not a TTY."""
    if os.environ.get("NO_COLOR"):
        return True
    if not sys.stdout.isatty():
        # Still allow when running in CI or pipes; keep colors off
        return True
    return False


USE_COLOR = not _no_color()


def _c(text: str, *codes: str) -> str:
    if not USE_COLOR:
        return text
    return "".join(codes) + text + C.RESET


def step(title: str) -> None:
    bar = "─" * 64
    print()
    print(_c(bar, C.BRIGHT_CYAN))
    print(_c(f"  {title}", C.BOLD, C.BRIGHT_CYAN))
    print(_c(bar, C.BRIGHT_CYAN))
    print()


def ok(msg: str) -> None:
    print(f"  {_c('✓', C.BOLD, C.BRIGHT_GREEN)} {msg}")


def warn(msg: str) -> None:
    print(f"  {_c('!', C.BOLD, C.BRIGHT_YELLOW)} {msg}")


def err(msg: str) -> None:
    print(f"  {_c('✗', C.BOLD, C.BRIGHT_RED)} {msg}")


def info(msg: str) -> None:
    print(f"  {_c(msg, C.DIM)}")


def heading(msg: str) -> None:
    print()
    print(_c(f"  {msg}", C.BOLD, C.BRIGHT_MAGENTA))
    print()


def key_value(key: str, value: str) -> None:
    k = _c(f"{key:<16}", C.CYAN)
    v = _c(str(value), C.WHITE)
    print(f"  {k}: {v}")


# ==================================================================
# Paths and constants
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


# ==================================================================
# PyYAML bootstrap (needed to read config.yaml)
# ==================================================================
def _ensure_yaml() -> Any:
    try:
        import yaml
        return yaml
    except ImportError:
        warn("PyYAML not found. Installing it for the system Python...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyyaml"],
            check=True,
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
        print()
        print("  DuckDB Portable Toolkit")
        print()
    print(_c("  A fully portable data + ML environment that runs inside", C.DIM))
    print(_c("  Jupyter and Streamlit. Works on Windows and Linux.", C.DIM))
    print()
def show_profile_table() -> None:
    heading("Available Installation Profiles")
    if USE_COLOR:
        # Header
        hdr = (
            f"  {_c('Option', C.BOLD, C.BRIGHT_WHITE):<20}"
            f"{_c('Profile', C.BOLD, C.BRIGHT_WHITE):<20}"
            f"{_c('Description', C.BOLD, C.BRIGHT_WHITE):<42}"
            f"{_c('Size', C.BOLD, C.BRIGHT_WHITE):>12}"
        )
        print(hdr)
        print(_c("  " + "─" * 90, C.DIM))
        for opt, name, desc, size in PROFILE_INFO:
            line = (
                f"  {_c(opt, C.BOLD, C.BRIGHT_CYAN):<20}"
                f"{_c(name, C.BRIGHT_MAGENTA):<20}"
                f"{desc:<42}"
                f"{_c(size, C.BRIGHT_GREEN):>12}"
            )
            print(line)
    else:
        print("  Option  Profile    Description                         Size")
        print("  " + "-" * 70)
        for opt, name, desc, size in PROFILE_INFO:
            print(f"  {opt:<7} {name:<10} {desc:<35} {size:>10}")
    print()


def prompt_profile_cli() -> str:
    """Ask the user which profile to install."""
    while True:
        print(_c("  Choose 1, 2, 3, or 4", C.BOLD))
        print(f"     {_c('1', C.BRIGHT_CYAN)} - light      (minimal)")
        print(f"     {_c('2', C.BRIGHT_CYAN)} - standard   {_c('(recommended)', C.DIM)}")
        print(f"     {_c('3', C.BRIGHT_CYAN)} - full       (everything)")
        print(f"     {_c('4', C.BRIGHT_CYAN)} - custom     (edit config first)")
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
        err(f"Invalid choice: '{choice}'. Enter 1, 2, 3, or 4.")
        print()


def prompt_existing_config() -> str:
    """Ask what to do when config.yaml already exists."""
    heading("config.yaml already exists")
    info(f"File: {CONFIG_FILE}")
    try:
        size = CONFIG_FILE.stat().st_size
        info(f"Size: {size} bytes")
    except Exception:
        pass
    print()
    print(_c("  What would you like to do?", C.BOLD))
    print(f"     {_c('K', C.BRIGHT_CYAN)} - keep the existing config and install")
    print(f"     {_c('O', C.BRIGHT_CYAN)} - overwrite it (choose a new profile)")
    print(f"     {_c('E', C.BRIGHT_CYAN)} - edit it first (exit and re-run)")
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
        err(f"Invalid choice: '{choice}'.")


def choose_profile(force: str | None = None) -> str:
    """Decide which profile to use. Returns a profile name."""
    if force:
        if force not in ("light", "standard", "full", "custom"):
            err(f"Unknown profile: {force}")
            sys.exit(1)
        ok(f"Using profile from CLI: {force}")
        return force

    # If config.yaml already exists, ask what to do
    if CONFIG_FILE.exists():
        decision = prompt_existing_config()
        if decision == "keep":
            return "keep"
        if decision == "edit":
            print()
            info(f"Edit {CONFIG_FILE} and run `python setup.py` again.")
            info(f"File location: {CONFIG_FILE}")
            sys.exit(0)
        # else: overwrite → fall through to profile selection

    show_profile_table()
    return prompt_profile_cli()


def apply_profile(profile: str) -> None:
    """Copy the chosen profile config to config.yaml."""
    if profile == "keep":
        ok("Using existing config.yaml")
        return

    src = PROFILES_DIR / f"config.{profile}.yaml"
    if not src.exists():
        err(f"Profile config not found: {src}")
        info(f"Expected file: {src}")
        info("Make sure the 'configs/' folder contains the profile files.")
        sys.exit(1)

    shutil.copy2(src, CONFIG_FILE)
    ok(f"Profile '{profile}' written to config.yaml")

    if profile == "custom":
        print()
        heading("Custom profile - edit your config")
        print(_c("  Next steps:", C.BOLD))
        print(f"     1. Open {_c(str(CONFIG_FILE), C.BRIGHT_CYAN)}")
        print(f"     2. Edit paths, packages, AI model, etc.")
        print(f"     3. Run {_c('python setup.py', C.BRIGHT_GREEN)} again")
        print()
        print(_c("  Common customizations:", C.BOLD))
        print(f"     • paths.project_root                 install on another drive")
        print(f"     • pytorch.build                      'cuda' for NVIDIA GPU")
        print(f"     • packages.*                         set to false to skip")
        print(f"     • ai.model                           different Ollama model")
        print(f"     • runtime.duckdb_memory_limit        match your RAM")
        print(f"     • mcp.db_path                        path to your .duckdb file")
        print()
        sys.exit(0)


# ==================================================================
# Config loading
# ==================================================================
def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise SystemExit(f"Missing {CONFIG_FILE}")
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
        self.venv_dir       = resolve(base, p["venv_dir"])
        self.duckdb_dir     = resolve(base, p["duckdb_dir"])
        self.extensions_dir = resolve(base, p["extensions_dir"])
        self.models_dir     = resolve(base, p["models_dir"])
        self.jobs_dir       = resolve(base, p["jobs_dir"])
        self.configs_dir    = resolve(base, p["configs_dir"])
        self.data_dir       = resolve(base, p["data_dir"])
        self.exports_dir    = resolve(base, p["exports_dir"])
        self.logs_dir       = resolve(base, p["logs_dir"])
        self.mlruns_dir     = resolve(base, p["mlruns_dir"])
        self.reports_dir    = resolve(base, p["reports_dir"])


# ==================================================================
# Download helpers
# ==================================================================
def download(url: str, dest: Path, retries: int = 3) -> None:
    info(f"downloading {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, retries + 1):
        try:
            urllib.request.urlretrieve(url, dest)
            size_mb = dest.stat().st_size / 1024 / 1024
            ok(f"saved {dest.name}  ({size_mb:.1f} MB)")
            return
        except Exception as exc:
            if attempt < retries:
                warn(f"attempt {attempt} failed: {exc}. retrying...")
                time.sleep(2 * attempt)
            else:
                err(f"download failed after {retries} attempts: {exc}")
                raise


def extract_zip(archive: Path, target: Path) -> None:
    with zipfile.ZipFile(archive) as z:
        z.extractall(target)
    archive.unlink()


def extract_tar_gz(archive: Path, target: Path) -> None:
    with tarfile.open(archive, "r:gz") as t:
        t.extractall(target)
    archive.unlink()


def make_executable(path: Path) -> None:
    if OS != "windows" and path.exists():
        os.chmod(path, 0o755)


def python_exe(paths: Paths) -> Path:
    return (paths.python_dir / "python.exe" if OS == "windows"
            else paths.python_dir / "bin" / "python3")


def venv_python(paths: Paths) -> Path:
    return (paths.venv_dir / "Scripts" / "python.exe" if OS == "windows"
            else paths.venv_dir / "bin" / "python")


def venv_pip(paths: Paths) -> Path:
    return (paths.venv_dir / "Scripts" / "pip.exe" if OS == "windows"
            else paths.venv_dir / "bin" / "pip")


# ==================================================================
# Installation steps
# ==================================================================
def create_dirs(paths: Paths) -> None:
    step("Creating directory structure")
    dirs = [
        paths.runtime_dir, paths.duckdb_dir, paths.extensions_dir,
        paths.models_dir, paths.jobs_dir, paths.configs_dir,
        paths.data_dir, paths.exports_dir, paths.logs_dir,
        paths.mlruns_dir, paths.reports_dir,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        rel = d.relative_to(paths.project_root)
        ok(f"{rel}")


def python_build_url(python_version: str) -> tuple[str, str]:
    release_tag = "20241016"
    base = ("https://github.com/astral-sh/python-build-standalone/"
            f"releases/download/{release_tag}")
    if OS == "windows":
        platform_tag = "x86_64-pc-windows-msvc"
    else:
        platform_tag = f"{ARCH}-unknown-linux-gnu"
    filename = (f"cpython-{python_version}+{release_tag}-"
                f"{platform_tag}-install_only.tar.gz")
    return f"{base}/{filename}", filename


def install_python(paths: Paths, cfg: dict) -> None:
    step(f"Installing portable Python {cfg['python']['version']}")
    if not cfg["setup"]["download_python"]:
        warn("skipped by config"); return
    py = python_exe(paths)
    if py.exists() and cfg["setup"]["skip_existing"]:
        r = subprocess.run([str(py), "--version"], capture_output=True, text=True)
        ver = r.stdout.strip() or r.stderr.strip()
        ok(f"already present: {ver}")
        return
    version = cfg["python"]["version"]
    url, archive_name = python_build_url(version)
    archive = paths.runtime_dir / archive_name
    download(url, archive)
    tmp_extract = paths.runtime_dir / "_tmp_python"
    if tmp_extract.exists():
        shutil.rmtree(tmp_extract, ignore_errors=True)
    tmp_extract.mkdir(parents=True, exist_ok=True)
    extract_tar_gz(archive, tmp_extract)
    src = tmp_extract / "python"
    if paths.python_dir.exists():
        shutil.rmtree(paths.python_dir, ignore_errors=True)
    if src.exists():
        shutil.move(str(src), str(paths.python_dir))
    else:
        shutil.move(str(tmp_extract), str(paths.python_dir))
    shutil.rmtree(tmp_extract, ignore_errors=True)
    make_executable(py)
    r = subprocess.run([str(py), "--version"], capture_output=True, text=True)
    ok(f"Python installed: {r.stdout.strip() or r.stderr.strip()}")


def create_venv(paths: Paths, cfg: dict) -> None:
    step("Creating virtual environment")
    if not cfg["setup"]["install_packages"]:
        warn("skipped by config"); return
    vpy = venv_python(paths)
    if vpy.exists() and cfg["setup"]["skip_existing"]:
        ok(f"venv already present: {vpy}")
        return
    py = python_exe(paths)
    if not py.exists():
        err(f"Python not found at {py}"); sys.exit(1)
    subprocess.run([str(py), "-m", "venv", str(paths.venv_dir)], check=True)
    ok(f"venv created at {paths.venv_dir}")
    # Upgrade pip via python -m pip (required by pip 24+)
    subprocess.run([str(vpy), "-m", "pip", "install", "--upgrade",
                    "pip", "setuptools", "wheel",
                    "--no-warn-script-location",
                    "--disable-pip-version-check"], check=True)
    ok("pip, setuptools, wheel upgraded")


def install_duckdb(paths: Paths, cfg: dict) -> None:
    step("Installing DuckDB CLI")
    if not cfg["setup"]["download_duckdb"]:
        warn("skipped by config"); return
    exe_name = "duckdb.exe" if OS == "windows" else "duckdb"
    exe_path = paths.duckdb_dir / exe_name
    if exe_path.exists() and cfg["setup"]["skip_existing"]:
        ok(f"already present: {exe_path.name}"); return
    duckdb_platform = {
        ("windows", "x86_64"): "windows-amd64",
        ("linux", "x86_64"):   "linux-amd64",
        ("linux", "aarch64"):  "linux-arm64",
    }.get((OS, ARCH), "linux-amd64")
    url = ("https://github.com/duckdb/duckdb/releases/latest/download/"
           f"duckdb_cli-{duckdb_platform}.zip")
    archive = paths.duckdb_dir / "duckdb.zip"
    download(url, archive)
    extract_zip(archive, paths.duckdb_dir)
    make_executable(exe_path)
    ok("DuckDB CLI ready")


PKG_GROUPS = {
    "core": ["duckdb", "pandas", "pyarrow", "numpy", "polars"],
    "jupyter": ["jupyterlab", "jupysql", "duckdb-engine", "sqlalchemy",
                "ipywidgets", "ipykernel"],
    "visualization": ["matplotlib", "seaborn", "plotly", "altair", "bokeh",
                      "holoviews", "kaleido"],
    "streamlit": ["streamlit", "streamlit-aggrid"],
    "eda": ["missingno", "ydata-profiling", "sweetviz", "k-eda",
            "autoviz", "dtale", "lazypredict", "sklearn-pandas"],
    "data_quality": ["great-expectations", "pandera"],
    "notebook_tools": ["papermill", "nbformat", "nbconvert", "jupyterlab-git"],
    "scheduling": ["schedule", "apscheduler"],
    "ml": ["scikit-learn", "xgboost", "lightgbm",
           "transformers", "datasets", "sentence-transformers"],
    "mlops": ["mlflow", "optuna"],
    "cloud": ["boto3", "openpyxl", "qvdrs[duckdb]"],
    "utilities": ["pyyaml", "requests", "tqdm", "loguru", "rich",
                  "humanize", "tabulate", "jinja2", "markdown", "pydantic",
                  "jupyter-ai", "mcp"],
}


def pip_install(vpip: str, package: str, retries: int = 3) -> bool:
    for attempt in range(1, retries + 1):
        result = subprocess.run(
            [vpip, "install", "--no-warn-script-location",
             "--disable-pip-version-check", "--timeout", "120", package],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            return True
        if attempt < retries:
            warn(f"retry {attempt}/{retries} for {package}")
            time.sleep(3 * attempt)
    return False


def install_packages(paths: Paths, cfg: dict) -> None:
    step("Installing Python packages")
    if not cfg["setup"]["install_packages"]:
        warn("skipped by config"); return
    vpip = str(venv_pip(paths))
    pytorch_build = cfg.get("pytorch", {}).get("build", "cpu").lower()
    cuda_version = cfg.get("pytorch", {}).get("cuda_version", "cu121")
    torch_index = (f"https://download.pytorch.org/whl/{cuda_version}"
                   if pytorch_build == "cuda"
                   else "https://download.pytorch.org/whl/cpu")
    enabled = cfg.get("packages", {})
    failed = []
    for group, pkgs in PKG_GROUPS.items():
        if not enabled.get(group, True):
            info(f"skipping group: {group}")
            continue
        heading(f"Package group: {group}")
        for pkg in pkgs:
            info(f"installing {pkg} ...")
            if pip_install(vpip, pkg):
                ok(pkg)
            else:
                err(f"{pkg} failed")
                failed.append(pkg)
    if enabled.get("ml", True):
        heading(f"PyTorch ({pytorch_build})")
        cmd = [vpip, "install", "--no-warn-script-location",
               "--disable-pip-version-check", "--timeout", "120",
               "torch", "torchvision", "--index-url", torch_index]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            ok("torch + torchvision")
        else:
            err("torch install failed")
            failed.extend(["torch", "torchvision"])
    if failed:
        heading("Packages that failed")
        for p in failed:
            err(p)
        print()
        info(f"retry with: {vpip} install {' '.join(failed)}")
    else:
        ok("all packages installed")


def install_extensions(paths: Paths, cfg: dict) -> None:
    step("Installing DuckDB extensions")
    if not cfg["setup"]["install_extensions"]:
        warn("skipped by config"); return
    exe = paths.duckdb_dir / ("duckdb.exe" if OS == "windows" else "duckdb")
    if not exe.exists():
        warn("DuckDB CLI not found, skipping extensions"); return
    ext = cfg.get("extensions", {})
    todo = ([(n, "core") for n in ext.get("core", [])] +
            [(n, "community") for n in ext.get("community", [])])
    for name, repo in todo:
        sql = (f"SET extension_directory='{paths.extensions_dir}'; "
               f"INSTALL {name} {'FROM community' if repo == 'community' else ''};")
        r = subprocess.run([str(exe), "-c", sql],
                           capture_output=True, text=True)
        if r.returncode == 0:
            ok(f"{name}  ({repo})")
        else:
            warn(f"{name}  ({repo}) - skipped")
    ok("extensions processed")


def install_ollama(paths: Paths, cfg: dict) -> None:
    ai_cfg = cfg.get("ai", {})
    if not ai_cfg.get("enabled", False):
        warn("AI assistant disabled in config")
        return
    step("Setting up local AI assistant (Ollama)")
    ollama = shutil.which("ollama")
    if not ollama:
        warn("Ollama not found in PATH.")
        info("Install Ollama manually: https://ollama.com/download")
        info(f"Then run: ollama pull {ai_cfg.get('model', 'qwen2.5-coder:3b')}")
        return
    model = ai_cfg.get("model", "qwen2.5-coder:3b")
    ok(f"Ollama found: {ollama}")
    if ai_cfg.get("auto_pull", True):
        info(f"Pulling model {model} (this may take a few minutes)...")
        r = subprocess.run([ollama, "pull", model],
                           capture_output=True, text=True)
        if r.returncode == 0:
            ok(f"model {model} ready")
        else:
            warn(f"could not pull {model}")
            if r.stderr:
                info(r.stderr[:200])


def install_mcp(paths: Paths, cfg: dict) -> None:
    step("Setting up MCP server for AI")
    mcp_cfg = cfg.get("mcp", {})
    if not mcp_cfg.get("enabled", False):
        warn("MCP server disabled in config")
        return
    mcp_dir = paths.project_root / "mcp"
    if not mcp_dir.exists():
        warn(f"MCP folder not found at {mcp_dir}")
        return
    ok(f"MCP server ready at mcp/")
    info(f"Database path : {mcp_cfg.get('db_path', ':memory:')}")
    info(f"Read-only     : {mcp_cfg.get('read_only', True)}")
    print()
    info("Client config (paste into your MCP client):")
    if OS == "windows":
        py = paths.venv_dir / "Scripts" / "python.exe"
    else:
        py = paths.venv_dir / "bin" / "python"
    info(f'  "command": "{py}"')
    info(f'  "args": ["mcp/server.py"]')


def generate_manifest(paths: Paths) -> None:
    step("Generating environment manifest")
    script = paths.project_root / "mcp" / "manifest_generator.py"
    if not script.exists():
        warn("manifest_generator.py not found")
        return
    vpy = str(venv_python(paths))
    r = subprocess.run([vpy, str(script)], capture_output=True, text=True)
    if r.returncode == 0:
        ok("manifest generated at runtime/manifest.md")
    else:
        warn("manifest generation failed")


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
    if not cfg["setup"]["create_config_files"]:
        warn("skipped by config"); return
    secrets = paths.configs_dir / "secrets.sql"
    if not secrets.exists():
        secrets.write_text(SECRETS_TEMPLATE, encoding="utf-8")
        ok(f"created configs/secrets.sql")
    else:
        ok(f"kept existing configs/secrets.sql")
    paths_json = paths.configs_dir / "paths.json"
    paths_json.write_text(
        json.dumps({k: str(v) for k, v in vars(paths).items()}, indent=2),
        encoding="utf-8",
    )
    ok(f"created configs/paths.json")


# ==================================================================
# Main
# ==================================================================
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Portable DuckDB Toolkit - Setup",
    )
    parser.add_argument(
        "--profile", "-p",
        choices=["light", "standard", "full", "custom"],
        help="Skip the profile prompt and install this profile directly",
    )
    args = parser.parse_args()

    print_banner()

    # 1. Choose profile
    profile = choose_profile(force=args.profile)
    apply_profile(profile)

    # 2. Load config
    cfg = load_config()
    paths = Paths(cfg)

    step("Configuration")
    key_value("OS", OS)
    key_value("Architecture", ARCH)
    key_value("Target Python", cfg["python"]["version"])
    key_value("Project root", str(paths.project_root))
    key_value("Runtime dir", str(paths.runtime_dir))
    key_value("PyTorch build", cfg.get("pytorch", {}).get("build", "cpu"))
    key_value("AI assistant", str(cfg.get("ai", {}).get("enabled", False)))
    key_value("DuckDB UI", str(cfg.get("duck_ui", {}).get("enabled", False)))
    key_value("MCP server", str(cfg.get("mcp", {}).get("enabled", False)))

    # 3. Install
    create_dirs(paths)
    install_python(paths, cfg)
    create_venv(paths, cfg)
    install_duckdb(paths, cfg)
    install_packages(paths, cfg)
    install_extensions(paths, cfg)
    install_ollama(paths, cfg)
    install_mcp(paths, cfg)
    generate_manifest(paths)
    write_configs(paths, cfg)

    # 4. Report
    print()
    bar = "═" * 64
    print(_c(bar, C.BOLD, C.BRIGHT_GREEN))
    print(_c("  ✓ Setup complete!", C.BOLD, C.BRIGHT_GREEN))
    print(_c(bar, C.BOLD, C.BRIGHT_GREEN))
    print()

    vpy = venv_python(paths)
    heading("Next steps")
    print(f"  {_c('1.', C.BOLD)} Launch JupyterLab:")
    print(f"     {_c(str(vpy) + ' -m jupyterlab', C.BRIGHT_CYAN)}")
    print()
    print(f"  {_c('2.', C.BOLD)} Open in your browser:")
    print(f"     {_c('http://localhost:8888', C.BRIGHT_CYAN)}")
    print()
    print(f"  {_c('3.', C.BOLD)} Open an example notebook:")
    print(f"     {_c('examples/01_basic_queries.py', C.BRIGHT_CYAN)}")
    print()
    print(f"  {_c('4.', C.BOLD)} Edit business context for the AI:")
    print(f"     {_c('mcp/context/business.md', C.BRIGHT_CYAN)}")
    print()
    print(f"  {_c('5.', C.BOLD)} Edit database credentials:")
    print(f"     {_c('configs/secrets.sql', C.BRIGHT_CYAN)}")
    print()
    print(f"  {_c('6.', C.BOLD)} Verify installation:")
    print(f"     {_c('python verify.py', C.BRIGHT_GREEN)}")
    print()


if __name__ == "__main__":
    main()