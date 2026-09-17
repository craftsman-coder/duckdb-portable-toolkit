# %% [markdown]
# # 13 - Data quality

# %%
import duckdb
import pandera as pa

con = duckdb.connect()
df = con.execute("SELECT * FROM range(1, 101) t(i)").fetchdf()

# %%
schema = pa.DataFrameSchema({
    "i": pa.Column(int, checks=[pa.Check.gt(0), pa.Check.lt(1000)]),
})
schema.validate(df)
print("Pandera validation passed.")

# %%
try:
    import great_expectations as gx
    context = gx.get_context()
    validator = context.sources.pandas_default.read_dataframe(df)
    validator.expect_column_values_to_be_between("i", min_value=1, max_value=100)
    validator.expect_column_values_to_be_unique("i")
    results = validator.validate()
    print("Great Expectations passed:", results["success"])
except ImportError:
    print("great-expectations not installed")