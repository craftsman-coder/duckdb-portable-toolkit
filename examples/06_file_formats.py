# %% [markdown]
# # 06 - Read/write every supported file format

# %%
import duckdb
from toolkit.config import EXTENSIONS_DIR

con = duckdb.connect()
con.execute(f"SET extension_directory='{EXTENSIONS_DIR}'")
con.execute("LOAD qvd; LOAD parquet; LOAD json;")

# %%
con.execute("COPY (SELECT 1 AS a, 'x' AS b) TO 'exports/demo.parquet' (FORMAT PARQUET)")
con.execute("COPY (SELECT 1 AS a, 'x' AS b) TO 'exports/demo.csv' (FORMAT CSV, HEADER)")
con.execute("COPY (SELECT 1 AS a, 'x' AS b) TO 'exports/demo.json' (FORMAT JSON)")
con.execute("COPY (SELECT 1 AS a, 'x' AS b) TO 'exports/demo.qvd' (FORMAT qvd)")

# %%
for path, reader in [
    ("exports/demo.parquet", "read_parquet"),
    ("exports/demo.csv",     "read_csv_auto"),
    ("exports/demo.json",    "read_json_auto"),
    ("exports/demo.qvd",     "read_qvd"),
]:
    print(path, "->")
    print(con.execute(f"SELECT * FROM {reader}('{path}')").fetchdf())
