"""Run multiple DuckDB queries in parallel."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

import duckdb

from toolkit.config import runtime


@dataclass
class QueryResult:
    query_id: str
    status: str
    elapsed: float = 0.0
    rows: int = 0
    data: Any = None
    file: str | None = None
    error: str | None = None
    attempts: int = 0


class ParallelRunner:
    def __init__(self, db_path=":memory:", max_workers=None,
                 retries=0, retry_delay=1.0, on_progress=None):
        self.db_path = str(db_path)
        self.max_workers = max_workers or runtime().get("duckdb_threads", 4)
        self.retries = retries
        self.retry_delay = retry_delay
        self.on_progress = on_progress
        self._conn = duckdb.connect(self.db_path)
        mem = runtime().get("duckdb_memory_limit")
        if mem:
            try:
                self._conn.execute(f"SET memory_limit='{mem}'")
            except Exception:
                pass

    def _execute_once(self, query_id, sql, write_to=None, fetch=True):
        cursor = self._conn.cursor()
        t0 = time.perf_counter()
        try:
            if write_to is not None:
                write_to.parent.mkdir(parents=True, exist_ok=True)
                cursor.execute(f"COPY ({sql}) TO '{write_to}' (FORMAT PARQUET)")
                return QueryResult(query_id, "ok",
                                   elapsed=time.perf_counter() - t0,
                                   file=str(write_to))
            df = cursor.execute(sql).fetchdf() if fetch else None
            return QueryResult(query_id, "ok",
                               elapsed=time.perf_counter() - t0,
                               rows=(len(df) if df is not None else 0),
                               data=df)
        except Exception as exc:
            return QueryResult(query_id, "error",
                               elapsed=time.perf_counter() - t0,
                               error=str(exc))
        finally:
            cursor.close()

    def _execute(self, *args, **kwargs):
        last = None
        for attempt in range(1 + self.retries):
            result = self._execute_once(*args, **kwargs)
            result.attempts = attempt + 1
            if result.status == "ok":
                return result
            last = result
            if attempt < self.retries:
                time.sleep(self.retry_delay * (2 ** attempt))
        return last

    def run(self, queries, write_to=None, fetch=True):
        write_to = write_to or [None] * len(queries)
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {
                pool.submit(self._execute, qid, sql, out, fetch): qid
                for (qid, sql), out in zip(queries, write_to)
            }
            for fut in as_completed(futures):
                res = fut.result()
                results.append(res)
                if self.on_progress:
                    self.on_progress(res)
        return sorted(results, key=lambda r: r.query_id)

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
