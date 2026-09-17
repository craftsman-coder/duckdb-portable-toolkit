# %% [markdown]
# # 10 - End-to-end lakehouse pipeline

# %%
import duckdb
from toolkit.config import EXTENSIONS_DIR
from toolkit.lakehouse import lance_write

con = duckdb.connect()
con.execute(f"SET extension_directory='{EXTENSIONS_DIR}'")

# %%
con.execute("""
    CREATE OR REPLACE TABLE clean_orders AS
    SELECT
        i                                    AS order_id,
        (i % 500) + 1                        AS customer_id,
        DATE '2025-01-01' + INTERVAL (i % 365) DAY AS order_date,
        ROUND(random() * 950 + 50, 2)        AS amount
    FROM range(1, 10001) t(i)
""")

# %%
con.execute("SELECT count(*) AS rows, sum(amount) AS total FROM clean_orders").fetchdf()

# %%
lance_write(con, "SELECT * FROM clean_orders",
            "exports/lance/clean_orders.lance", mode="overwrite")
print("Done -> exports/lance/clean_orders.lance")