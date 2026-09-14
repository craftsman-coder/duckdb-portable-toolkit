#!/usr/bin/env python3
"""Verify that the Portable DuckDB Toolkit is fully installed."""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()
OS = platform.system().lower()
CHECKS = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


def _py(root):
    return (root / "python_portable" / "python.exe" if OS == "windows"
            else root / "python_portable" / "bin" / "python")


@check("python_portable exists")
def _c1():
    return _py(HERE).exists(), str(_py(HERE))


@check("duckdb_portable exists")
def _c2():
    name = "duckdb.exe" if OS == "windows" else "duckdb"
    p = HERE / "duckdb_portable" / name
    return p.exists(), str(p)


@check("extensions_dir exists")
def _c3():
    p = HERE / "duckdb_portable" / "extensions"
    return p.exists(), str(p)


@check("config.yaml exists")
def _c4():
    p = HERE / "config.yaml"
    return p.exists(), str(p)


@check("secrets.sql exists")
def _c5():
    p = HERE / "configs" / "secrets.sql"
    return p.exists(), str(p)


@check("DuckDB Python module")
def _c6():
    py = _py(HERE)
    if not py.exists():
        return False, "python not found"
    r = subprocess.run([str(py), "-c", "import duckdb; print(duckdb.__version__)"],
                       capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip() or r.stderr.strip()


@check("pandas")
def _c7():
    py = _py(HERE)
    r = subprocess.run([str(py), "-c", "import pandas; print(pandas.__version__)"],
                       capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip() or r.stderr.strip()


@check("PyTorch")
def _c8():
    py = _py(HERE)
    r = subprocess.run(
        [str(py), "-c",
         "import torch; print(torch.__version__, torch.cuda.is_available())"],
        capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip() or r.stderr.strip()


@check("MLflow")
def _c9():
    py = _py(HERE)
    r = subprocess.run([str(py), "-c", "import mlflow; print(mlflow.__version__)"],
                       capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip() or r.stderr.strip()


@check("Jupyter")
def _c10():
    py = _py(HERE)
    r = subprocess.run([str(py), "-m", "jupyter", "--version"],
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout.strip().splitlines()[0] if r.stdout else "")


@check("Streamlit")
def _c11():
    py = _py(HERE)
    r = subprocess.run([str(py), "-m", "streamlit", "version"],
                       capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip() or r.stderr.strip()


@check("DuckDB extensions loaded")
def _c12():
    py = _py(HERE)
    if not py.exists():
        return False, "python not found"
    ext = HERE / "duckdb_portable" / "extensions"
    code = (
        "import duckdb;"
        "con=duckdb.connect();"
        f"con.execute(\"SET extension_directory='{ext}'\");"
        "n=con.execute('SELECT count(*) FROM duckdb_extensions() WHERE installed').fetchone()[0];"
        "print(n)"
    )
    r = subprocess.run([str(py), "-c", code], capture_output=True, text=True)
    return r.returncode == 0, f"{r.stdout.strip()} extensions"


def main():
    print("\n" + "=" * 64)
    print("  Portable DuckDB Toolkit - Verification")
    print("=" * 64)
    passed = 0
    for name, fn in CHECKS:
        try:
            okv, info = fn()
        except Exception as exc:
            okv, info = False, f"exception: {exc}"
        mark = "[ok]" if okv else "[XX]"
        print(f"  {mark}  {name:30s}  {info}")
        if okv:
            passed += 1
    print("\n" + "=" * 64)
    print(f"  {passed}/{len(CHECKS)} checks passed")
    print("=" * 64 + "\n")
    if passed < len(CHECKS):
        sys.exit(1)


if __name__ == "__main__":
    main()
