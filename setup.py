#!/usr/bin/env python3
"""Portable DuckDB Toolkit - one-click setup (config-driven)."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


def _ensure_yaml() -> Any:
    try:
        import yaml
        return yaml
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml"], check=True)
        import yaml
        return yaml


yaml = _ensure_yaml()
HERE = Path(__file__).parent.resolve()
CONFIG_FILE = HERE / "config.yaml"
OS = platform.system().lower()
ARCH_RAW = platform.machine().lower()
ARCH = {"x86_64": "amd64", "amd64": "amd64",
        "aarch64": "arm64", "arm64": "arm64"}.get(ARCH_RAW, "amd64")


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
        self.python_dir     = resolve(base, p["python_dir"])
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


def step(t: str) -> None:
    print(f"\n{'=' * 64}\n  {t}\n{'=' * 64}")


def ok(m: str) -> None:
    print(f"  [ok]  {m}")


def warn(m: str) -> None:
    print(f"  [!!]  {m}")


def download(url: str, dest: Path) -> None:
    print(f"  downloading {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    ok(f"saved {dest}")


def extract_zip(archive: Path, target: Path) -> None:
    with zipfile.ZipFile(archive) as z:
        z.extractall(target)
    archive.unlink()


def make_executable(path: Path) -> None:
    if OS != "windows" and path.exists():
        os.chmod(path, 0o755)


def python_exe(paths: Paths) -> Path:
    return (paths.python_dir / "python.exe" if OS == "windows"
            else paths.python_dir / "bin" / "python")


def pip_exe(paths: Paths) -> Path:
    return (paths.python_dir / "Scripts" / "pip.exe" if OS == "windows"
            else paths.python_dir / "bin" / "pip")


def create_dirs(paths: Paths) -> None:
    step("Creating directory structure")
    for d in [paths.python_dir, paths.duckdb_dir, paths.extensions_dir,
              paths.models_dir, paths.jobs_dir, paths.configs_dir,
              paths.data_dir, paths.exports_dir, paths.logs_dir,
              paths.mlruns_dir, paths.reports_dir]:
        d.mkdir(parents=True, exist_ok=True)
        ok(str(d))


def install_duckdb(paths: Paths, cfg: dict) -> None:
    step("Installing DuckDB CLI")
    if not cfg["setup"]["download_duckdb"]:
        warn("skipped"); return
    exe_name = "duckdb.exe" if OS == "windows" else "duckdb"
    exe_path = paths.duckdb_dir / exe_name
    if exe_path.exists() and cfg["setup"]["skip_existing"]:
        ok(f"already present: {exe_path}"); return
    url = ("https://github.com/duckdb/duckdb/releases/latest/download/"
           f"duckdb_cli-{OS}-{ARCH}.zip")
    archive = paths.duckdb_dir / "duckdb.zip"
    download(url, archive)
    extract_zip(archive, paths.duckdb_dir)
    make_executable(exe_path)
    ok("DuckDB CLI ready")


def install_miniconda(paths: Paths, cfg: dict) -> None:
    step("Installing portable Python (Miniconda)")
    if not cfg["setup"]["download_miniconda"]:
        warn("skipped"); return
    py = python_exe(paths)
    if py.exists() and cfg["setup"]["skip_existing"]:
        ok(f"already present: {py}"); return
    if OS == "windows":
        url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
        installer = paths.python_dir / "miniconda.exe"
        download(url, installer)
        subprocess.run([str(installer), "/S", f"/D={paths.python_dir}",
                        "/AddToPath=0", "/RegisterPython=0"], check=True)
    else:
        url = f"https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-{ARCH}.sh"
        installer = paths.python_dir / "miniconda.sh"
        download(url, installer)
        make_executable(installer)
        subprocess.run(f'bash "{installer}" -b -p "{paths.python_dir}"',
                       shell=True, check=True)
    installer.unlink(missing_ok=True)
    ok("Miniconda installed")


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
                  "humanize", "tabulate", "jinja2", "markdown", "pydantic"],
}


def install_packages(paths: Paths, cfg: dict) -> None:
    step("Installing Python packages")
    if not cfg["setup"]["install_packages"]:
        warn("skipped"); return
    pip = str(pip_exe(paths))
    subprocess.run([pip, "install", "--upgrade", "pip"], check=True)

    pytorch_build = cfg.get("pytorch", {}).get("build", "cpu").lower()
    cuda_version = cfg.get("pytorch", {}).get("cuda_version", "cu121")
    torch_index = (f"https://download.pytorch.org/whl/{cuda_version}"
                   if pytorch_build == "cuda"
                   else "https://download.pytorch.org/whl/cpu")

    enabled = cfg.get("packages", {})
    for group, pkgs in PKG_GROUPS.items():
        if not enabled.get(group, True):
            print(f"  -- skipping group '{group}'")
            continue
        print(f"\n  == group: {group}")
        for pkg in pkgs:
            print(f"     installing {pkg} ...")
            subprocess.run([pip, "install", pkg], check=True)

    if enabled.get("ml", True):
        print(f"\n  == PyTorch ({pytorch_build})")
        subprocess.run([pip, "install", "torch", "torchvision",
                        "--index-url", torch_index], check=True)
    ok("all packages installed")


def install_extensions(paths: Paths, cfg: dict) -> None:
    step("Installing DuckDB extensions")
    if not cfg["setup"]["install_extensions"]:
        warn("skipped"); return
    exe = paths.duckdb_dir / ("duckdb.exe" if OS == "windows" else "duckdb")
    if not exe.exists():
        warn(f"DuckDB CLI not found at {exe}"); return
    ext = cfg.get("extensions", {})
    todo = [(n, "core") for n in ext.get("core", [])] + \
           [(n, "community") for n in ext.get("community", [])]
    for name, repo in todo:
        sql = (f"SET extension_directory='{paths.extensions_dir}'; "
               f"INSTALL {name} {'FROM community' if repo == 'community' else ''};")
        r = subprocess.run([str(exe), "-c", sql], capture_output=True, text=True)
        (ok if r.returncode == 0 else warn)(f"{name} ({repo})")
    ok("extensions processed")


SECRETS_TEMPLATE = '''-- Database secrets - fill in your credentials.
-- This file is git-ignored.

CREATE SECRET IF NOT EXISTS ora (
    TYPE oracle,
    HOST 'oracle-host',
    PORT 1521,
    SERVICE_NAME 'ORCLPDB1',
    USER 'user',
    PASSWORD 'pass'
);

CREATE SECRET IF NOT EXISTS pg (
    TYPE postgres,
    HOST 'pg-host',
    PORT 5432,
    DATABASE 'mydb',
    USER 'user',
    PASSWORD 'pass'
);

CREATE SECRET IF NOT EXISTS mysql (
    TYPE mysql,
    HOST 'mysql-host',
    PORT 3306,
    DATABASE 'mydb',
    USER 'user',
    PASSWORD 'pass'
);
'''


def write_configs(paths: Paths, cfg: dict) -> None:
    step("Writing configuration files")
    if not cfg["setup"]["create_config_files"]:
        warn("skipped"); return
    secrets = paths.configs_dir / "secrets.sql"
    if not secrets.exists():
        secrets.write_text(SECRETS_TEMPLATE, encoding="utf-8")
        ok(f"created {secrets}")
    else:
        ok(f"kept existing {secrets}")
    paths_json = paths.configs_dir / "paths.json"
    paths_json.write_text(json.dumps({
        k: str(v) for k, v in vars(paths).items()
    }, indent=2), encoding="utf-8")
    ok(f"created {paths_json}")


def main() -> None:
    print("\n" + "=" * 64)
    print("  Portable DuckDB Toolkit - Setup")
    print("=" * 64)
    print(f"  OS           : {OS}")
    print(f"  Architecture : {ARCH}")
    cfg = load_config()
    paths = Paths(cfg)
    print(f"  Project root : {paths.project_root}")
    print(f"  Python dir   : {paths.python_dir}")
    print(f"  DuckDB dir   : {paths.duckdb_dir}")
    print(f"  PyTorch      : {cfg.get('pytorch', {}).get('build', 'cpu')}")
    create_dirs(paths)
    install_duckdb(paths, cfg)
    install_miniconda(paths, cfg)
    install_packages(paths, cfg)
    install_extensions(paths, cfg)
    write_configs(paths, cfg)
    print("\n" + "=" * 64)
    print("  Setup complete!")
    print("=" * 64)
    jup = (paths.python_dir / "Scripts" / "jupyter-lab.exe" if OS == "windows"
           else paths.python_dir / "bin" / "jupyter-lab")
    st = (paths.python_dir / "Scripts" / "streamlit.exe" if OS == "windows"
          else paths.python_dir / "bin" / "streamlit")
    print(f"\n  Launch Jupyter  :  {jup}")
    print(f"  Launch Streamlit:  {st} run dashboards/01_orders_dashboard.py")


if __name__ == "__main__":
    main()
