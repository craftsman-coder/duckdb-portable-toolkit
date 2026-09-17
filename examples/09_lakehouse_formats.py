# %% [markdown]
# # 09 - Lakehouse formats

# %%
import duckdb
from toolkit.config import EXTENSIONS_DIR
from toolkit.lakehouse import lance_write, lance_scan

con = duckdb.connect()
con.execute(f"SET extension_directory='{EXTENSIONS_DIR}'")

# %%
lance_write(con, "SELECT * FROM range(1000) t(i)", "exports/lance/numbers.lance")
lance_scan(con, "exports/lance/numbers.lance", limit=5)