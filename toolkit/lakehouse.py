"""Helpers for lakehouse formats."""

from __future__ import annotations

from pathlib import Path

import duckdb

from toolkit.config import EXTENSIONS_DIR

def _connect():
    con = duckdb.connect()
    con.execute(f"SET extension_directory='{EXTENSIONS_DIR}'")
    return con

def _load(con, *exts):
    for e in exts:
        con.execute(f"LOAD {e};")

def iceberg_attach(con, catalog_uri, warehouse, *, alias="ice", token=None, extra=None):
    _load(con, "iceberg")
    opts = ["TYPE iceberg", f"ENDPOINT '{catalog_uri}'"]
    if token:
        opts.append(f"TOKEN '{token}'")
    if extra:
        for k, v in extra.items():
            opts.append(f"{k} '{v}'")
    con.execute(f"ATTACH '{warehouse}' AS {alias} ({', '.join(opts)});")

def ducklake_attach(con, metadata_path, data_path, *, alias="dl"):
    _load(con, "ducklake")
    metadata_path = Path(metadata_path)
    data_path = Path(data_path)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.mkdir(parents=True, exist_ok=True)
    con.execute(f"ATTACH 'ducklake:{metadata_path}' AS {alias} (DATA_PATH '{data_path}');")
    con.execute(f"USE {alias};")

def delta_scan(con, table_uri):
    _load(con, "delta")
    return con.execute(f"SELECT * FROM delta_scan('{table_uri}')").fetchdf()

def lance_scan(con, dataset_uri, limit=None):
    _load(con, "lance")
    sql = f"SELECT * FROM '{dataset_uri}'"
    if limit:
        sql += f" LIMIT {limit}"
    return con.execute(sql).fetchdf()

def lance_write(con, sql, dataset_uri, *, mode="overwrite"):
    _load(con, "lance")
    Path(dataset_uri).parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY ({sql}) TO '{dataset_uri}' (FORMAT lance, MODE '{mode}')")

def paimon_scan(con, warehouse, database, table):
    _load(con, "paimon")
    return con.execute(
        f"SELECT * FROM paimon_scan('{warehouse}', '{database}', '{table}')"
    ).fetchdf()

def list_tables(con, catalog):
    return con.execute(f"SHOW TABLES FROM {catalog};").fetchdf()

def describe_table(con, qualified_name):
    return con.execute(f"DESCRIBE {qualified_name};").fetchdf()