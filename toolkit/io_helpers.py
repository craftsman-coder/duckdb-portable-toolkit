"""Helpers for reading/writing common file formats."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from toolkit.config import EXTENSIONS_DIR

def _new_con():
    con = duckdb.connect()
    con.execute(f"SET extension_directory='{EXTENSIONS_DIR}'")
    return con

def to_parquet(con, sql, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY ({sql}) TO '{path}' (FORMAT PARQUET)")

def to_csv(con, sql, path, header=True):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY ({sql}) TO '{path}' (FORMAT CSV, HEADER {str(header).lower()})")

def to_qvd(con, sql, path):
    con.execute("LOAD qvd;")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY ({sql}) TO '{path}' (FORMAT qvd)")

def read_any(path):
    con = _new_con()
    p = str(path).lower()
    if p.endswith(".parquet"):
        return con.execute(f"SELECT * FROM read_parquet('{path}')").fetchdf()
    if p.endswith(".csv"):
        return con.execute(f"SELECT * FROM read_csv_auto('{path}')").fetchdf()
    if p.endswith(".json"):
        return con.execute(f"SELECT * FROM read_json_auto('{path}')").fetchdf()
    if p.endswith(".qvd"):
        con.execute("LOAD qvd;")
        return con.execute(f"SELECT * FROM read_qvd('{path}')").fetchdf()
    raise ValueError(f"Unsupported extension: {path}")