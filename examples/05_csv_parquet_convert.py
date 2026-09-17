# %% [markdown]
# # 05 - Convert between CSV and Parquet

# %%
import duckdb
from toolkit.io_helpers import to_parquet, to_csv

con = duckdb.connect()

# %%
to_parquet(con, "SELECT 1 AS a, 'x' AS b UNION ALL SELECT 2, 'y'",
           "data/sample.parquet")

# %%
to_csv(con, "SELECT * FROM read_parquet('data/sample.parquet')",
       "data/sample.csv", header=True)

# %%
con.execute("SELECT * FROM read_csv_auto('data/sample.csv')").fetchdf()