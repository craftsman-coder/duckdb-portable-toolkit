"""Runtime config loader for the Portable DuckDB Toolkit."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent.resolve()
CONFIG_FILE = ROOT / "config.yaml"


@lru_cache(maxsize=1)
def load() -> dict:
    """Load config.yaml once and cache it."""
    with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@lru_cache(maxsize=1)
def paths() -> dict:
    """Return resolved paths as a dict of Path objects."""
    cfg = load()
    base = Path(cfg["paths"]["project_root"]).expanduser()
    if not base.is_absolute():
        base = (ROOT / base).resolve()

    def r(v):
        p = Path(v).expanduser()
        return p if p.is_absolute() else (base / p).resolve()

    p = cfg["paths"]
    return {
        "project_root": base,
        "runtime_dir":    r(p["runtime_dir"]),
        "python_dir":     r(p["python_dir"]),
        "duckdb_dir":     r(p["duckdb_dir"]),
        "extensions_dir": r(p["extensions_dir"]),
        "models_dir":     r(p["models_dir"]),
        "jobs_dir":       r(p.get("jobs_dir", "jobs")),
        "configs_dir":    r(p.get("configs_dir", "configs")),
        "data_dir":       r(p.get("data_dir", "data")),
        "exports_dir":    r(p.get("exports_dir", "exports")),
        "logs_dir":       r(p.get("logs_dir", "logs")),
        "mlruns_dir":     r(p.get("mlruns_dir", "mlruns")),
        "reports_dir":    r(p.get("reports_dir", "reports")),
    }


P = paths()
ROOT_DIR = P["project_root"]
RUNTIME_DIR = P["runtime_dir"]
PYTHON_DIR = P["python_dir"]
DUCKDB_DIR = P["duckdb_dir"]
EXTENSIONS_DIR = P["extensions_dir"]
MODELS_DIR = P["models_dir"]
JOBS_DIR = P["jobs_dir"]
CONFIGS_DIR = P["configs_dir"]
DATA_DIR = P["data_dir"]
EXPORTS_DIR = P["exports_dir"]
LOGS_DIR = P["logs_dir"]
MLRUNS_DIR = P["mlruns_dir"]
REPORTS_DIR = P["reports_dir"]

DUCKDB_EXE = DUCKDB_DIR / ("duckdb.exe" if os.name == "nt" else "duckdb")
SECRETS_FILE = CONFIGS_DIR / "secrets.sql"


def runtime() -> dict:
    """Return the `runtime` section of config.yaml."""
    return load().get("runtime", {})


def scheduler_cfg() -> dict:
    """Return the `scheduler` section of config.yaml."""
    return load().get("scheduler", {})


def ai_cfg() -> dict:
    """Return the `ai` section of config.yaml."""
    return load().get("ai", {})


def mcp_cfg() -> dict:
    """Return the `mcp` section of config.yaml."""
    return load().get("mcp", {})


def duck_ui_cfg() -> dict:
    """Return the `duck_ui` section of config.yaml."""
    return load().get("duck_ui", {})


def venv_dir() -> Path:
    """Deprecated ; kept for backward compatibility. Returns python_dir."""
    return PYTHON_DIR