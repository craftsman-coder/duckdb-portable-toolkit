#!/usr/bin/env python3
"""
Fix three things:
  1. Replace the banner in setup.py (tries multiple patterns)
  2. Restore jobs/example_daily_export.py
  3. Restore the .gitkeep files in empty runtime folders
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent.resolve()


# ==================================================================
# 1. Fix banner in setup.py
# ==================================================================
def fix_banner() -> None:
    setup_file = ROOT / "setup.py"
    if not setup_file.exists():
        print("  [!!] setup.py not found")
        return

    content = setup_file.read_text(encoding="utf-8")

    # The full print_banner function
    new_func = (
        "def print_banner() -> None:\n"
        "    print()\n"
        "    if USE_COLOR:\n"
        '        banner = r"""\n'
        "  ____             _         ____  ____\n"
        " |  _ \\ _   _  ___| | __    |  _ \\| __ )\n"
        " | | | | | | |/ __| |/ /    | | | |  _ \\\n"
        " | |_| | |_| | (__|   <     | |_| | |_) |\n"
        " |____/ \\__,_|\\___|_|\\_\\    |____/|____/\n"
        "\n"
        "        p o r t a b l e   t o o l k i t\n"
        '"""\n'
        "        print(_c(banner, C.BRIGHT_CYAN))\n"
        "    else:\n"
        "        print()\n"
        '        print("  DuckDB Portable Toolkit")\n'
        "        print()\n"
        '    print(_c("  A fully portable data + ML environment that runs inside", C.DIM))\n'
        '    print(_c("  Jupyter and Streamlit. Works on Windows and Linux.", C.DIM))\n'
        "    print()\n"
    )

    # Pattern A: whole function
    pattern_a = re.compile(
        r"^def print_banner\([^\n]*\)[^\n]*:\n[\s\S]*?(?=^def |^class |\Z)",
        re.MULTILINE,
    )
    if pattern_a.search(content):
        content = pattern_a.sub(new_func, content, count=1)
        setup_file.write_text(content, encoding="utf-8")
        print("  [ok] print_banner() replaced (Pattern A)")
        return

    # Pattern B: banner inside (double-quote)
    pattern_b = re.compile(
        r'\s+banner = r"""[\s\S]*?"""',
        re.MULTILINE,
    )
    if pattern_b.search(content):
        art = (
            '        banner = r"""\n'
            "  ____             _         ____  ____\n"
            " |  _ \\ _   _  ___| | __    |  _ \\| __ )\n"
            " | | | | | | |/ __| |/ /    | | | |  _ \\\n"
            " | |_| | |_| | (__|   <     | |_| | |_) |\n"
            " |____/ \\__,_|\\___|_|\\_\\    |____/|____/\n"
            "\n"
            "        p o r t a b l e   t o o l k i t\n"
            '"""'
        )
        content = pattern_b.sub("\n" + art, content, count=1)
        setup_file.write_text(content, encoding="utf-8")
        print("  [ok] banner replaced (Pattern B)")
        return

    # Pattern C: banner inside (single-quote)
    pattern_c = re.compile(
        r"\s+banner = r'''[\s\S]*?'''",
        re.MULTILINE,
    )
    if pattern_c.search(content):
        art = (
            '        banner = r"""\n'
            "  ____             _         ____  ____\n"
            " |  _ \\ _   _  ___| | __    |  _ \\| __ )\n"
            " | | | | | | |/ __| |/ /    | | | |  _ \\\n"
            " | |_| | |_| | (__|   <     | |_| | |_) |\n"
            " |____/ \\__,_|\\___|_|\\_\\    |____/|____/\n"
            "\n"
            "        p o r t a b l e   t o o l k i t\n"
            '"""'
        )
        content = pattern_c.sub("\n" + art, content, count=1)
        setup_file.write_text(content, encoding="utf-8")
        print("  [ok] banner replaced (Pattern C)")
        return

    print("  [!!] no banner found - none of the 3 patterns matched")
    print("       Send me the print_banner section of your setup.py.")


# ==================================================================
# 2. Restore jobs/example_daily_export.py
# ==================================================================
def restore_example_job() -> None:
    target = ROOT / "jobs" / "example_daily_export.py"
    if target.exists():
        print(f"  [ok] {target.relative_to(ROOT)} already exists")
        return

    content = (
        '"""\n'
        "Example job: daily Oracle -> Parquet export.\n"
        "\n"
        "Every job file must define a `run()` function.\n"
        '"""\n'
        "\n"
        "from datetime import date\n"
        "from pathlib import Path\n"
        "\n"
        "import duckdb\n"
        "\n"
        "from toolkit.config import EXTENSIONS_DIR, CONFIGS_DIR\n"
        "\n"
        "\n"
        "def run() -> None:\n"
        '    output = Path("exports/daily_sales.parquet")\n'
        "    output.parent.mkdir(parents=True, exist_ok=True)\n"
        "\n"
        "    con = duckdb.connect()\n"
        "    con.execute(f\"SET extension_directory='{EXTENSIONS_DIR}'\")\n"
        "    con.execute(\"LOAD oracle_scanner;\")\n"
        "\n"
        '    secrets = CONFIGS_DIR / "secrets.sql"\n'
        "    if secrets.exists():\n"
        '        con.execute(secrets.read_text(encoding="utf-8"))\n'
        "\n"
        "    con.execute(f\"\"\"\n"
        "        COPY (\n"
        "            SELECT *\n"
        "            FROM oracle_query('ora',\n"
        "                 'SELECT * FROM sales WHERE sale_date = CURRENT_DATE')\n"
        "        ) TO '{output}' (FORMAT PARQUET)\n"
        '    """)\n'
        '    print(f"[{date.today()}] wrote {output}")\n'
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"  [ok] restored {target.relative_to(ROOT)}")


# ==================================================================
# 3. Restore .gitkeep files
# ==================================================================
def restore_gitkeeps() -> None:
    folders = ["configs", "data", "exports", "logs", "mlruns", "reports"]
    for name in folders:
        folder = ROOT / name
        folder.mkdir(parents=True, exist_ok=True)
        keep = folder / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")
            print(f"  [ok] restored {keep.relative_to(ROOT)}")
        else:
            print(f"  [ok] {keep.relative_to(ROOT)} already exists")


# ==================================================================
# Main
# ==================================================================
def main() -> None:
    print("\n=== Fixing ===")
    print("\n1. setup.py banner")
    fix_banner()

    print("\n2. jobs/example_daily_export.py")
    restore_example_job()

    print("\n3. .gitkeep files")
    restore_gitkeeps()

    print("\n" + "=" * 60)
    print("  Done.")
    print("=" * 60)
    print()
    print("  Next:")
    print("    git add .")
    print('    git commit -m "fix: banner, example job, gitkeep files"')
    print("    git push -u origin main")
    print()


if __name__ == "__main__":
    main()