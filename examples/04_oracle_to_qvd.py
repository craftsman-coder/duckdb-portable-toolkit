# %% [markdown]
# # 04 - Extract from Oracle and write to QVD

# %%
import duckdb
from toolkit.io_helpers import to_qvd
from toolkit.config import EXTENSIONS_DIR, CONFIGS_DIR

con = duckdb.connect()
con.execute(f"SET extension_directory='{EXTENSIONS_DIR}'")
con.execute("LOAD qvd;")
con.execute("LOAD oracle_scanner;")

# %%
secrets = CONFIGS_DIR / "secrets.sql"
if secrets.exists():
    con.execute(secrets.read_text(encoding="utf-8"))

# %%
to_qvd(
    con,
    "SELECT * FROM oracle_query('ora', 'SELECT * FROM sales WHERE ROWNUM <= 100')",
    "exports/oracle_sales.qvd",
)
print("Done -> exports/oracle_sales.qvd")