"""Browse any DuckDB file."""

from pathlib import Path

import duckdb
import streamlit as st

from _common import page_header, aggrid_table

page_header("Data explorer", "Open a DuckDB file and browse its tables.")

db_path = st.text_input("DuckDB file path",
                        value=str(Path("analytics.duckdb").resolve()))
if not Path(db_path).exists():
    st.warning("File not found. Create one first.")
    st.stop()

con = duckdb.connect(db_path, read_only=True)
tables = con.execute("""
    SELECT table_schema, table_name
    FROM information_schema.tables
    ORDER BY 1, 2
""").fetchdf()

if tables.empty:
    st.info("No tables.")
    st.stop()

schemas = ["(all)"] + sorted(tables["table_schema"].unique().tolist())
schema_choice = st.selectbox("Schema", schemas)
filtered = tables if schema_choice == "(all)" else tables[tables["table_schema"] == schema_choice]
choices = [f"{r.table_schema}.{r.table_name}" for r in filtered.itertuples()]
table_choice = st.selectbox("Table", choices)

st.divider()
info = con.execute(f"DESCRIBE {table_choice}").fetchdf()
st.subheader("Schema")
st.dataframe(info, use_container_width=True)

limit = st.slider("Row limit", 10, 5000, 100, step=10)
df = con.execute(f"SELECT * FROM {table_choice} LIMIT {limit}").fetchdf()
st.subheader(f"Data - first {limit} rows")
aggrid_table(df, page_size=25)