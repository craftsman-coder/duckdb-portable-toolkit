"""Example job: daily Oracle -> Parquet export."""

from datetime import date
from pathlib import Path

import duckdb

from toolkit.config import EXTENSIONS_DIR, CONFIGS_DIR


def run() -> None:
    output = Path("exports/daily_sales.parquet")
    output.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET extension_directory='{EXTENSIONS_DIR}'")
    con.execute("LOAD oracle_scanner;")
    secrets = CONFIGS_DIR / "secrets.sql"
    if secrets.exists():
        con.execute(secrets.read_text(encoding="utf-8"))
    con.execute(f"""
        COPY (
            SELECT *
            FROM oracle_query('ora',
                 'SELECT * FROM sales WHERE sale_date = CURRENT_DATE')
        ) TO '{output}' (FORMAT PARQUET)
    """)
    print(f"[{date.today()}] wrote {output}")
