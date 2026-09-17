"""Browse Iceberg, Delta, Lance, DuckLake."""

import duckdb
import streamlit as st

from _common import page_header, aggrid_table, extensions_dir

page_header("Lakehouse viewer", "Browse Iceberg, Delta, Lance, DuckLake.")

con = duckdb.connect()
con.execute(f"SET extension_directory='{extensions_dir()}'")

fmt = st.selectbox("Format", ["Iceberg (REST)", "Delta", "Lance", "DuckLake"])

if fmt == "Iceberg (REST)":
    try:
        con.execute("LOAD iceberg;")
    except Exception as exc:
        st.error(f"iceberg extension missing: {exc}")
        st.stop()
    uri = st.text_input("Catalog URI", value="http://localhost:8181/api/catalog")
    warehouse = st.text_input("Warehouse", value="lakehouse")
    token = st.text_input("Bearer token (optional)", type="password")
    if st.button("Attach"):
        try:
            opts = [f"TYPE iceberg", f"ENDPOINT '{uri}'"]
            if token:
                opts.append(f"TOKEN '{token}'")
            con.execute(f"ATTACH '{warehouse}' AS ice ({', '.join(opts)});")
            st.success("Attached.")
        except Exception as exc:
            st.error(str(exc))

elif fmt == "Delta":
    uri = st.text_input("Delta table URI", value="exports/delta/orders")
    if st.button("Load"):
        try:
            con.execute("LOAD delta;")
            df = con.execute(f"SELECT * FROM delta_scan('{uri}') LIMIT 500").fetchdf()
            aggrid_table(df)
        except Exception as exc:
            st.error(str(exc))

elif fmt == "Lance":
    uri = st.text_input("Lance dataset", value="exports/lance/numbers.lance")
    if st.button("Load"):
        try:
            con.execute("LOAD lance;")
            df = con.execute(f"SELECT * FROM '{uri}' LIMIT 500").fetchdf()
            aggrid_table(df)
        except Exception as exc:
            st.error(str(exc))

else:
    metadata = st.text_input("Metadata file", value="data/ducklake/metadata.ducklake")
    data_path = st.text_input("Data folder", value="data/ducklake/data")
    if st.button("Attach"):
        try:
            con.execute("LOAD ducklake;")
            con.execute(f"ATTACH 'ducklake:{metadata}' AS dl (DATA_PATH '{data_path}');")
            tables = con.execute("SHOW TABLES FROM dl;").fetchdf()
            st.dataframe(tables, use_container_width=True)
        except Exception as exc:
            st.error(str(exc))