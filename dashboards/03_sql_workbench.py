"""Run arbitrary SQL."""

import streamlit as st

from _common import (page_header, run_sql, aggrid_table,
                     get_connection, extensions_dir)


page_header("SQL workbench", "Write and run SQL against DuckDB.")
con = get_connection(":memory:")
con.execute(f"SET extension_directory='{extensions_dir()}'")

with st.sidebar:
    st.header("Extensions")
    ext = st.selectbox("Load extension", [
        "(none)", "parquet", "json", "icu", "httpfs",
        "iceberg", "delta", "ducklake", "lance",
        "qvd", "pbix",
        "oracle_scanner", "postgres_scanner",
        "mysql_scanner", "sqlite_scanner",
    ])
    if st.button("Load") and ext != "(none)":
        try:
            con.execute(f"LOAD {ext}")
            st.success(f"Loaded {ext}")
        except Exception as exc:
            st.error(str(exc))

example = """SELECT
    (ARRAY['A','B','C','D'])[1 + (i % 4)] AS category,
    ROUND(random() * 1000, 2)             AS amount
FROM range(1, 1001) t(i)
"""
sql = st.text_area("SQL", value=example, height=220)
if st.button("Run", type="primary"):
    df = run_sql(con, sql)
    if df is not None:
        st.success(f"{len(df):,} rows returned.")
        aggrid_table(df, page_size=25)
