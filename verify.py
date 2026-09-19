#!/usr/bin/env python3
"""Verify that the DuckDB Toolkit is fully installed."""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()
OS = platform.system().lower()


def _rel(p: Path) -> str:
    """Return a relative path when possible, else the absolute path."""
    try:
        return str(p.relative_to(HERE))
    except ValueError:
        return str(p)


# ==================================================================
# Colored output
# ==================================================================
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
    return (HERE / "runtime" / "python" / "python.exe"
            if OS == "windows"
            else HERE / "runtime" / "python" / "bin" / "python3")


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def _load_config():
    """Read config.yaml if present."""
    cfg_file = HERE / "config.yaml"
    if not cfg_file.exists():
        return {}
    try:
        import yaml
        with open(cfg_file, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        return {}


# ==================================================================
# Base installation checks
# ==================================================================
@check("runtime/python exists")
def _c1():
    p = (HERE / "runtime" / "python" /
         ("python.exe" if OS == "windows" else "bin/python3"))
    return p.exists(), _rel(p)


@check("runtime/duckdb CLI exists")
def _c3():
    name = "duckdb.exe" if OS == "windows" else "duckdb"
    p = HERE / "runtime" / "duckdb" / name
    return p.exists(), _rel(p)


@check("config.yaml exists")
def _c4():
    return (HERE / "config.yaml").exists(), ""


@check("secrets.sql exists")
def _c5():
    return (HERE / "configs" / "secrets.sql").exists(), ""


# ==================================================================
# Python environment
# ==================================================================
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


# ==================================================================
# AI assistant (llama.cpp)
# ==================================================================
@check("llama.cpp binary")
def _c18():
    cfg = _load_config()
    ai_cfg = cfg.get("ai", {})
    if not ai_cfg.get("enabled", False):
        return True, "disabled in config"
    if ai_cfg.get("provider") != "llama.cpp":
        return True, f"provider is '{ai_cfg.get('provider')}', not llama.cpp"

    bin_dir = HERE / ai_cfg.get("bin_dir", "runtime/llama.cpp")
    exe_name = "llama-server.exe" if OS == "windows" else "llama-server"
    server_exe = bin_dir / exe_name

    if not server_exe.exists():
        return False, f"missing {server_exe.relative_to(HERE)}"

    # Try to get version
    try:
        r = subprocess.run([str(server_exe), "--version"],
                           capture_output=True, text=True, timeout=5)
        ver = (r.stdout.strip() or r.stderr.strip()).split("\n")[0][:60]
        return True, f"present ({ver or 'version unknown'})"
    except Exception:
        return True, f"present at {server_exe.relative_to(HERE)}"


@check("AI model (GGUF)")
def _c19():
    cfg = _load_config()
    ai_cfg = cfg.get("ai", {})
    if not ai_cfg.get("enabled", False):
        return True, "disabled in config"
    if ai_cfg.get("provider") != "llama.cpp":
        return True, "provider is not llama.cpp"

    model_cfg = ai_cfg.get("model", {})
    model_dir = HERE / model_cfg.get("dir", "runtime/models")
    filename = model_cfg.get("filename", "")
    if not filename:
        return False, "no model configured"

    model_path = model_dir / filename
    if not model_path.exists():
        return False, f"missing {filename}"

    size_gb = model_path.stat().st_size / (1024 ** 3)
    return True, f"{filename} ({size_gb:.2f} GB)"


@check("AI provider config")
def _c20():
    cfg = _load_config()
    ai_cfg = cfg.get("ai", {})
    if not ai_cfg.get("enabled", False):
        return True, "disabled"
    provider = ai_cfg.get("provider", "?")
    host = ai_cfg.get("host", "?")
    port = ai_cfg.get("port", "?")
    return True, f"{provider} @ {host}:{port}"


# ==================================================================
# MCP server
# ==================================================================
@check("MCP server files")
def _c21():
    server = HERE / "mcp" / "server.py"
    ctx = HERE / "mcp" / "context" / "business.md"
    caps = HERE / "mcp" / "capabilities.md"
    missing = [p.name for p in (server, ctx, caps) if not p.exists()]
    if missing:
        return False, f"missing: {', '.join(missing)}"
    return True, "server.py + context + capabilities"


@check("runtime/manifest.md")
def _c22():
    p = HERE / "runtime" / "manifest.md"
    if not p.exists():
        return False, "not generated (run mcp/manifest_generator.py)"
    size = p.stat().st_size
    return True, f"{size} bytes"


# ==================================================================
# DuckDB extensions
# ==================================================================
@check("DuckDB extensions")
def _c_extensions():
    """Count installed DuckDB extensions (recursively)."""
    ext_dir = HERE / "runtime" / "duckdb" / "extensions"

    # Count .duckdb_extension files recursively
    files = list(ext_dir.rglob("*.duckdb_extension")) if ext_dir.exists() else []
    count = len(files)

    if count == 0:
        return False, "no extensions found"

    # Find the actual platform subfolder for display
    plat_dir = None
    for f in files:
        if f.parent != ext_dir:
            plat_dir = f.parent
            break

    if plat_dir:
        rel = plat_dir.relative_to(HERE)
        return True, f"{count} extensions in {rel}"
    return True, f"{count} extensions"


# ==================================================================
# Main
# ==================================================================


@check("Optional clients")
def _c_optional():
    """Check which optional client packages are available."""
    from importlib.metadata import version, PackageNotFoundError
    import subprocess

    found = []
    missing = []
    packages = [
        ("kafka", "kafka-python"),
        ("trino", "trino"),
        ("openai", "openai"),
        ("litellm", "litellm"),
    ]
    for module, pkg in packages:
        r = _run([str(_py()), "-c", f"import {module}"])
        if r.returncode == 0:
            try:
                v = version(pkg)
            except PackageNotFoundError:
                v = "installed"
            found.append(f"{module} {v}")
        else:
            missing.append(module)

    if found:
        info_str = ", ".join(found)
        if missing:
            info_str += " | missing: " + ", ".join(missing)
        return True, info_str
    return False, "no optional clients installed"


def main():
    print()
    heading("DuckDB Toolkit - Verification")

    passed = 0
    failed = []
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
            failed.append(name)

    print()
    total = len(CHECKS)
    if passed == total:
        heading(f"All {total} checks passed")
        info("Your toolkit is ready. Launch JupyterLab and start working.")
        sys.exit(0)
    else:
        heading(f"{passed}/{total} checks passed")
        info("Failed checks:")
        for name in failed:
            info(f"  - {name}")
        print()
        info("Common fixes:")
        info("  - Run 'python setup.py' to install missing components")
        info("  - Check config.yaml for path typos")
        info("  - For AI issues: verify ai.enabled and ai.provider in config.yaml")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()