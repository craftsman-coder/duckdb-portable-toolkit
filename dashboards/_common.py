"""Shared helpers for all Streamlit dashboards."""

from __future__ import annotations

from pathlib import Path

import duckdb
import streamlit as st

from toolkit.config import EXTENSIONS_DIR, CONFIGS_DIR, ROOT_DIR, runtime


def project_root() -> Path:
    return ROOT_DIR


def extensions_dir() -> Path:
    return EXTENSIONS_DIR


def secrets_file() -> Path:
    return CONFIGS_DIR / "secrets.sql"


@st.cache_resource
def get_connection(db_path: str = ":memory:") -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(db_path)
    con.execute(f"SET extension_directory='{EXTENSIONS_DIR}'")
    mem = runtime().get("duckdb_memory_limit")
    if mem:
        try:
            con.execute(f"SET memory_limit='{mem}'")
        except Exception:
            pass
    return con


def load_secrets(con):
    sf = secrets_file()
    if sf.exists():
        con.execute(sf.read_text(encoding="utf-8"))


def page_header(title: str, subtitle: str = "") -> None:
    st.set_page_config(page_title=title, layout="wide")
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def kpi_row(items):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def run_sql(con, sql: str):
    try:
        return con.execute(sql).fetchdf()
    except Exception as exc:
        st.error(f"SQL error: {exc}")
        return None


def show_table(df, page_size: int = 25) -> None:
    if df is None or df.empty:
        st.info("No rows to display.")
        return
    st.dataframe(df, use_container_width=True,
                 height=min(600, 40 + 35 * min(len(df), page_size)))


def aggrid_table(df, page_size: int = 25) -> None:
    try:
        from st_aggrid import AgGrid, GridOptionsBuilder
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=False,
                                paginationPageSize=page_size)
        gb.configure_default_column(filter=True, sortable=True, resizable=True)
        AgGrid(df, gridOptions=gb.build(), height=500)
    except ImportError:
        show_table(df, page_size=page_size)
