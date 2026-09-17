"""
User-friendly maintenance functions.

Use these inside a Jupyter notebook to:

  - install a new Python package (online or offline)
  - install a new DuckDB extension (online or offline)
  - download a package/extension for use on an offline machine
  - change the AI model in config.yaml
  - refresh the AI-visible manifest

All functions use the portable venv and portable DuckDB, so they
work without touching the system Python.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from toolkit.config import (
    DUCKDB_EXE,
    EXTENSIONS_DIR,
    ROOT_DIR,
    VENV_DIR,
)

# ------------------------------------------------------------------
# Internal paths
# ------------------------------------------------------------------
def _venv_pip() -> Path:
    return (VENV_DIR / "Scripts" / "pip.exe" if sys.platform == "win32"
            else VENV_DIR / "bin" / "pip")

def _venv_python() -> Path:
    return (VENV_DIR / "Scripts" / "python.exe" if sys.platform == "win32"
            else VENV_DIR / "bin" / "python")

def _manifest_script() -> Path:
    return ROOT_DIR / "mcp" / "manifest_generator.py"

def _config_file() -> Path:
    return ROOT_DIR / "config.yaml"

# ==================================================================
# Python packages
# ==================================================================
def install_python_package(package: str) -> bool:
    """
    Install a Python package into the portable venv.

    Example:
        install_python_package("statsmodels")
        install_python_package("seaborn==0.13.2")
    """
    pip = _venv_pip()
    if not pip.exists():
        print(f"pip not found at {pip}. Run setup.py first.")
        return False

    print(f"Installing {package} ...")
    r = subprocess.run(
        [str(pip), "install", "--no-warn-script-location",
         "--disable-pip-version-check", "--timeout", "120", package],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        print(f"  [ok] {package} installed")
        refresh_ai_docs()
        return True
    print(f"  [XX] {package} failed")
    if r.stderr:
        print("       " + r.stderr.strip().splitlines()[-1])
    return False

def list_python_packages() -> list[dict]:
    """Return a list of installed Python packages as {name, version}."""
    import json
    py = _venv_python()
    if not py.exists():
        return []
    r = subprocess.run([str(py), "-m", "pip", "list", "--format=json"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return []
    try:
        return json.loads(r.stdout)
    except Exception:
        return []

# ==================================================================
# Offline: download / install Python packages
# ==================================================================
def download_python_package(package: str,
                            dest: Path | str = "offline/wheels") -> bool:
    """
    Download a package and all its dependencies as wheels.

    Run this on a machine WITH internet, then copy the folder to the
    offline machine and use install_python_package_offline().

    Example:
        download_python_package("statsmodels")
    """
    dest = Path(dest)
    if not dest.is_absolute():
        dest = ROOT_DIR / dest
    dest.mkdir(parents=True, exist_ok=True)

    pip = _venv_pip()
    if not pip.exists():
        print(f"pip not found at {pip}.")
        return False

    print(f"Downloading {package} to {dest} ...")
    r = subprocess.run(
        [str(pip), "download", package, "-d", str(dest)],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        print(f"  [ok] wheels saved to {dest}")
        print(f"       Copy this folder to the offline machine,")
        print(f"       then run install_python_package_offline('{package}')")
        return True
    print(f"  [XX] download failed")
    if r.stderr:
        print("       " + r.stderr.strip().splitlines()[-1])
    return False

def install_python_package_offline(
    package: str,
    source: Path | str = "offline/wheels",
) -> bool:
    """
    Install a Python package from a local folder of wheels (no internet).

    Example:
        install_python_package_offline("statsmodels")
    """
    src = Path(source)
    if not src.is_absolute():
        src = ROOT_DIR / src
    if not src.exists():
        print(f"Folder not found: {src}")
        print("Did you download the wheels first?")
        return False

    pip = _venv_pip()
    if not pip.exists():
        print(f"pip not found at {pip}.")
        return False

    print(f"Installing {package} from {src} ...")
    r = subprocess.run(
        [str(pip), "install", "--no-index",
         f"--find-links={src}", package,
         "--no-warn-script-location",
         "--disable-pip-version-check"],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        print(f"  [ok] {package} installed offline")
        refresh_ai_docs()
        return True
    print(f"  [XX] install failed")
    if r.stderr:
        print("       " + r.stderr.strip().splitlines()[-1])
    return False

# ==================================================================
# DuckDB extensions
# ==================================================================
def install_duckdb_extension(name: str, community: bool = False) -> bool:
    """
    Install a DuckDB extension into the portable extension folder.

    Example:
        install_duckdb_extension("httpfs")
        install_duckdb_extension("qvd", community=True)
    """
    if not DUCKDB_EXE.exists():
        print(f"DuckDB CLI not found at {DUCKDB_EXE}.")
        return False

    src = "FROM community" if community else ""
    sql = (f"SET extension_directory='{EXTENSIONS_DIR}'; "
           f"INSTALL {name} {src};")
    print(f"Installing DuckDB extension: {name} ...")
    r = subprocess.run([str(DUCKDB_EXE), "-c", sql],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  [ok] {name} installed")
        refresh_ai_docs()
        return True
    print(f"  [XX] {name} failed")
    if r.stderr:
        print("       " + r.stderr.strip().splitlines()[-1])
    return False

def list_duckdb_extensions() -> list[dict]:
    """List installed DuckDB extensions."""
    import json
    if not DUCKDB_EXE.exists():
        return []
    sql = (f"SET extension_directory='{EXTENSIONS_DIR}'; "
           "SELECT extension_name, description "
           "FROM duckdb_extensions() WHERE installed "
           "ORDER BY extension_name;")
    r = subprocess.run([str(DUCKDB_EXE), "-json", "-c", sql],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return []
    try:
        return json.loads(r.stdout)
    except Exception:
        return []

# ==================================================================
# Offline: download DuckDB extensions
# ==================================================================
def download_duckdb_extension(
    name: str,
    dest: Path | str = "offline/extensions",
    community: bool = False,
) -> bool:
    """
    Download a DuckDB extension as a .duckdb_extension file.

    Run this on a machine WITH internet, then copy the file to the
    offline machine's runtime/duckdb/extensions/ folder.

    Example:
        download_duckdb_extension("httpfs")
        download_duckdb_extension("qvd", community=True)
    """
    dest = Path(dest)
    if not dest.is_absolute():
        dest = ROOT_DIR / dest
    dest.mkdir(parents=True, exist_ok=True)

    if not DUCKDB_EXE.exists():
        print(f"DuckDB CLI not found at {DUCKDB_EXE}.")
        return False

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        src = "FROM community" if community else ""
        sql = (f"SET extension_directory='{tmp_path}'; "
               f"INSTALL {name} {src};")
        print(f"Downloading DuckDB extension: {name} ...")
        r = subprocess.run([str(DUCKDB_EXE), "-c", sql],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  [XX] download failed")
            if r.stderr:
                print("       " + r.stderr.strip().splitlines()[-1])
            return False

        found = False
        for f in tmp_path.rglob("*.duckdb_extension"):
            shutil.copy2(f, dest / f.name)
            print(f"  [ok] saved {dest / f.name}")
            found = True
            break
        if not found:
            print("  [XX] extension file not found after install")
            return False

    print()
    print("  On the OFFLINE machine, copy the .duckdb_extension file to:")
    print(f"     {EXTENSIONS_DIR}")
    print("  Then load it with:")
    print(f"     LOAD {name};")
    return True

# ==================================================================
# AI model switching
# ==================================================================
def change_ai_model(model_name: str) -> bool:
    """
    Change the AI model in config.yaml.

    Example:
        change_ai_model("qwen2.5-coder:7b")
        change_ai_model("qwen3:8b")
    """
    cfg_file = _config_file()
    if not cfg_file.exists():
        print(f"Config file not found: {cfg_file}")
        return False

    try:
        import yaml
    except ImportError:
        print("PyYAML not available in this session.")
        return False

    text = cfg_file.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}

    if "ai" not in data:
        data["ai"] = {}
    old = data["ai"].get("model", "(none)")
    data["ai"]["model"] = model_name
    if "enabled" not in data["ai"]:
        data["ai"]["enabled"] = True

    pattern = re.compile(
        r"(^ai:\s*$[\s\S]*?^\s+model:\s*)(['\"]?)([^'\"\n]+)(\2)",
        re.MULTILINE,
    )
    if pattern.search(text):
        new_text = pattern.sub(
            lambda mo: mo.group(1) + mo.group(2) + model_name + mo.group(4),
            text,
            count=1,
        )
    else:
        new_text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    cfg_file.write_text(new_text, encoding="utf-8")
    print(f"  [ok] AI model changed from '{old}' to '{model_name}'")
    print()
    print("  To pull and start using the model, run:")
    print()
    print("  For GPU acceleration, see docs/AI_MODELS.md")
    return True

# ==================================================================
# Refresh AI-visible docs
# ==================================================================
def refresh_ai_docs() -> None:
    """
    Regenerate the environment manifest so the AI knows about new
    packages and extensions.
    """
    script = _manifest_script()
    if not script.exists():
        print("  (manifest generator not found)")
        return
    py = _venv_python()
    if not py.exists():
        return
    r = subprocess.run([str(py), str(script)], capture_output=True, text=True)
    if r.returncode == 0:
        print("  [ok] runtime/manifest.md refreshed")

def show_capabilities_tips() -> None:
    """Print a short note about editing the AI-visible Markdown files."""
    print()
    print("=" * 60)
    print("  AI-visible Markdown files")
    print("=" * 60)
    print()
    print("  The AI reads these files to understand your environment.")
    print("  Edit them whenever you want to teach the AI something new.")
    print()
    print("  1) Business context (tables, rules, metrics)")
    print(f"     mcp/context/business.md")
    print()
    print("  2) AI capabilities (what it can do, style guide)")
    print(f"     mcp/capabilities.md")
    print()
    print("  3) Environment manifest (auto-generated)")
    print(f"     runtime/manifest.md")
    print("     ^ refreshed automatically when you install packages")
    print()
    print("  Tip: after editing business.md, no restart is needed.")
    print("       The MCP server reads it on every request.")
    print()
    print("  Example: to tell the AI that 'amount' is in Rials, add to")
    print("  business.md:")
    print("     - All monetary columns are in Iranian Rials (IRR).")
    print()