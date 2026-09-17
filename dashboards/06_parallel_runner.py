"""Run many queries in parallel."""

import sys
import time
from pathlib import Path

import streamlit as st

from _common import page_header

page_header("Parallel query runner", "Run multiple DuckDB queries at once.")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from toolkit.parallel import ParallelRunner

num = st.slider("Number of queries", 2, 10, 4)
workers = st.slider("Max workers", 1, 8, 4)

defaults = [
    "SELECT sum(i) AS total FROM range(10000000) t(i)",
    "SELECT avg(i) AS mean FROM range(10000000) t(i)",
    "SELECT max(i) AS mx  FROM range(10000000) t(i)",
    "SELECT min(i) AS mn  FROM range(10000000) t(i)",
]

queries = []
for i in range(num):
    default = defaults[i] if i < len(defaults) else "SELECT 1"
    q = st.text_area(f"Query {i+1}", value=default, height=80, key=f"q{i}")
    queries.append((f"q{i+1}", q))

if st.button("Run in parallel", type="primary"):
    runner = ParallelRunner("parallel_demo.duckdb", max_workers=workers)
    t0 = time.perf_counter()
    results = runner.run(queries)
    total = time.perf_counter() - t0
    runner.close()

    st.success(f"Finished in {total:.2f}s")
    st.dataframe([
        {"query_id": r.query_id, "status": r.status,
         "elapsed_sec": round(r.elapsed, 3),
         "rows": r.rows, "error": r.error or ""}
        for r in results
    ], use_container_width=True)

    for r in results:
        with st.expander(f"Result - {r.query_id} ({r.status})"):
            if r.status == "ok" and r.data is not None:
                st.dataframe(r.data, use_container_width=True)
            else:
                st.error(r.error)