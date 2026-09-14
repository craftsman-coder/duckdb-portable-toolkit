# %% [markdown]
# # 12 - Lightweight EDA

# %%
import duckdb
con = duckdb.connect()
df = con.execute("""
    SELECT
        i                                       AS id,
        ROUND(random() * 100, 2)                AS amount,
        (ARRAY['A','B','C','D'])[1 + (i % 4)]   AS category,
        CASE WHEN i % 10 = 0 THEN NULL
             ELSE ROUND(random() * 50, 2) END    AS maybe_null
    FROM range(1, 1001) t(i)
""").fetchdf()

# %%
import missingno as msno
import matplotlib.pyplot as plt
msno.matrix(df)
plt.show()

# %%
import pandera as pa
schema = pa.DataFrameSchema({
    "id": pa.Column(int, checks=pa.Check.gt(0)),
    "amount": pa.Column(float, checks=pa.Check.ge(0)),
})
try:
    schema.validate(df)
    print("Schema validation passed.")
except pa.errors.SchemaError as exc:
    print("Schema validation failed:", exc)
