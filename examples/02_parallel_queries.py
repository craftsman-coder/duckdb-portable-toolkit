# %% [markdown]
# # 02 - Run many queries in parallel

# %%
from toolkit.parallel import ParallelRunner

# %%
with ParallelRunner("demo.duckdb", max_workers=4) as runner:
    queries = [
        ("q1", "SELECT 1 AS n, 'first'  AS label"),
        ("q2", "SELECT 2 AS n, 'second' AS label"),
        ("q3", "SELECT 3 AS n, 'third'  AS label"),
        ("q4", "SELECT 4 AS n, 'fourth' AS label"),
    ]
    results = runner.run(queries)

for r in results:
    print(r.query_id, r.status, f"{r.elapsed:.3f}s", r.rows)