#!/usr/bin/env python3
"""Verify that the Portable DuckDB Toolkit is fully installed."""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()
OS = platform.system().lower()


def _setup_colors():
    try:
        from rich.console import Console
        console = Console()
        def ok(m): console.print(f"  [bold green]✓[/bold green] {m}")
        def err(m): console.print(f"  [bold red]✗[/bold red] {m}")
        def heading(m): console.print(f"\n[bold cyan]{m}[/bold cyan]\n")
        def info(m): console.print(f"  [dim]{m}[/dim]")
        return ok, err, heading, info
    except ImportError:
        def ok(m): print(f"  [ok]  {m}")
        def err(m): print(f"  [XX]  {m}")
        def heading(m): print(f"\n=== {m} ===\n")
        def info(m): print(f"  {m}")
        return ok, err, heading, info


ok, err, heading, info = _setup_colors()
CHECKS = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


def _py():
    return (HERE / "runtime" / "venv" / "Scripts" / "python.exe"
            if OS == "windows"
            else HERE / "runtime" / "venv" / "bin" / "python")


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


@check("runtime/python exists")
def _c1():
    p = (HERE / "runtime" / "python" /
         ("python.exe" if OS == "windows" else "bin/python3"))
    return p.exists(), str(p.relative_to(HERE))


@check("runtime/venv exists")
def _c2():
    return _py().exists(), str(_py().relative_to(HERE))


@check("runtime/duckdb CLI exists")
def _c3():
    name = "duckdb.exe" if OS == "windows" else "duckdb"
    p = HERE / "runtime" / "duckdb" / name
    return p.exists(), str(p.relative_to(HERE))


@check("config.yaml exists")
def _c4():
    return (HERE / "config.yaml").exists(), ""


@check("secrets.sql exists")
def _c5():
    return (HERE / "configs" / "secrets.sql").exists(), ""


@check("Python version")
def _c6():
    r = _run([str(_py()), "--version"])
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


@check("duckdb (Python)")
def _c7():
    r = _run([str(_py()), "-c", "import duckdb; print(duckdb.__version__)"])
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


@check("pandas")
def _c8():
    r = _run([str(_py()), "-c", "import pandas; print(pandas.__version__)"])
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


@check("numpy")
def _c9():
    r = _run([str(_py()), "-c", "import numpy; print(numpy.__version__)"])
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


@check("jupyterlab")
def _c10():
    r = _run([str(_py()), "-m", "jupyterlab", "--version"])
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


@check("streamlit")
def _c11():
    r = _run([str(_py()), "-m", "streamlit", "version"])
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


@check("matplotlib")
def _c12():
    r = _run([str(_py()), "-c", "import matplotlib; print(matplotlib.__version__)"])
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


@check("scikit-learn")
def _c13():
    r = _run([str(_py()), "-c", "import sklearn; print(sklearn.__version__)"])
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


@check("PyTorch")
def _c14():
    r = _run([str(_py()), "-c",
              "import torch; print(torch.__version__, torch.cuda.is_available())"])
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


@check("MLflow")
def _c15():
    r = _run([str(_py()), "-c", "import mlflow; print(mlflow.__version__)"])
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


@check("jupyter-ai")
def _c16():
    r = _run([str(_py()), "-c", "import jupyter_ai; print('ok')"])
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip() or "ok")


@check("mcp package")
def _c17():
    r = _run([str(_py()), "-c", "import mcp; print('ok')"])
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip() or "ok")


@check("Ollama")
def _c18():
    import shutil
    p = shutil.which("ollama")
    return (True, p) if p else (False, "not installed")


@check("MCP server files")
def _c19():
    server = HERE / "mcp" / "server.py"
    ctx = HERE / "mcp" / "context" / "business.md"
    caps = HERE / "mcp" / "capabilities.md"
    missing = [p.name for p in (server, ctx, caps) if not p.exists()]
    if missing:
        return False, f"missing: {', '.join(missing)}"
    return True, "server.py + context + capabilities"


@check("runtime/manifest.md")
def _c20():
    p = HERE / "runtime" / "manifest.md"
    if not p.exists():
        return False, "not generated (run mcp/manifest_generator.py)"
    size = p.stat().st_size
    return True, f"{size} bytes"


@check("DuckDB extensions")
def _c21():
    ext = HERE / "runtime" / "duckdb" / "extensions"
    code = (
        "import duckdb;"
        "con=duckdb.connect();"
        f"con.execute(\"SET extension_directory='{ext}'\");"
        "n=con.execute('SELECT count(*) FROM duckdb_extensions() WHERE installed').fetchone()[0];"
        "print(n)"
    )
    r = _run([str(_py()), "-c", code])
    return r.returncode == 0, f"{r.stdout.strip()} extensions"


def main():
    print()
    heading("Portable DuckDB Toolkit - Verification")
    passed = 0
    for name, fn in CHECKS:
        try:
            okv, i = fn()
        except Exception as exc:
            okv, i = False, f"exception: {exc}"
        if okv:
            ok(f"{name:26s}  {i}")
            passed += 1
        else:
            err(f"{name:26s}  {i}")
    print()
    heading(f"{passed}/{len(CHECKS)} checks passed")
    sys.exit(0 if passed == len(CHECKS) else 1)


if __name__ == "__main__":
    main()