# %% [markdown]
# # 01 - Basic DuckDB queries in Jupyter

# %%
import duckdb
import pandas as pd

con = duckdb.connect()
df = pd.DataFrame({
    "product": ["A", "B", "C", "A", "B"],
    "amount":  [100, 200, 150, 300, 250],
    "region":  ["north", "north", "south", "south", "north"],
})
con.register("sales", df)

# %%
con.execute("""
    SELECT region, product, SUM(amount) AS total
    FROM sales
    GROUP BY region, product
    ORDER BY total DESC
""").fetchdf()