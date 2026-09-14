"""Runtime config loader."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent.resolve()
CONFIG_FILE = ROOT / "config.yaml"


@lru_cache(maxsize=1)
def load() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@lru_cache(maxsize=1)
def paths() -> dict:
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
        "python_dir": r(p["python_dir"]),
        "duckdb_dir": r(p["duckdb_dir"]),
        "extensions_dir": r(p["extensions_dir"]),
        "models_dir": r(p["models_dir"]),
        "jobs_dir": r(p["jobs_dir"]),
        "configs_dir": r(p["configs_dir"]),
        "data_dir": r(p["data_dir"]),
        "exports_dir": r(p["exports_dir"]),
        "logs_dir": r(p["logs_dir"]),
        "mlruns_dir": r(p["mlruns_dir"]),
        "reports_dir": r(p["reports_dir"]),
    }


P = paths()
ROOT_DIR = P["project_root"]
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
    return load().get("runtime", {})


def scheduler_cfg() -> dict:
    return load().get("scheduler", {})
