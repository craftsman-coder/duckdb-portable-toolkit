"""Preview CSV / Parquet / JSON / QVD."""

from pathlib import Path

import duckdb
import streamlit as st

from _common import page_header, aggrid_table, extensions_dir


page_header("File inspector", "Preview CSV, Parquet, JSON, QVD.")

con = duckdb.connect()
con.execute(f"SET extension_directory='{extensions_dir()}'")
con.execute("LOAD parquet; LOAD json;")
try:
    con.execute("LOAD qvd;")
except Exception:
    pass

uploaded = st.file_uploader("Upload a file",
                            type=["csv", "parquet", "json", "qvd"])
sample_path = st.text_input("...or paste a path on disk", value="")

path = None
if uploaded is not None:
    tmp = Path("uploads")
    tmp.mkdir(exist_ok=True)
    path = tmp / uploaded.name
    path.write_bytes(uploaded.read())
elif sample_path:
    path = Path(sample_path)

if path is None or not path.exists():
    st.info("Upload a file or enter a valid path.")
    st.stop()

suffix = path.suffix.lower()
readers = {
    ".parquet": "read_parquet",
    ".csv": "read_csv_auto",
    ".json": "read_json_auto",
    ".qvd": "read_qvd",
}
if suffix not in readers:
    st.error(f"Unsupported: {suffix}")
    st.stop()

limit = st.slider("Row limit", 10, 5000, 100, step=10)
try:
    df = con.execute(f"SELECT * FROM {readers[suffix]}('{path}') LIMIT {limit}").fetchdf()
except Exception as exc:
    st.error(str(exc))
    st.stop()

st.subheader(f"{path.name} - {len(df):,} rows previewed")
aggrid_table(df, page_size=25)
st.subheader("Column summary")
st.dataframe(df.describe(include="all").transpose(), use_container_width=True)
