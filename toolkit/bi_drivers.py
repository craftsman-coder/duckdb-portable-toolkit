"""
BI driver helpers for DuckDB.

Manage ODBC and JDBC drivers so BI tools (Tableau, Power BI,
Qlik Sense) can connect to your DuckDB databases.
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

from toolkit.config import DUCKDB_DIR, ROOT_DIR


OS_NAME = platform.system().lower()


def _drivers_dir() -> Path:
    """Return the drivers directory path."""
    return DUCKDB_DIR / "drivers"


# ------------------------------------------------------------------
# Paths to drivers
# ------------------------------------------------------------------
def jdbc_path() -> Path:
    """Return the path to the JDBC driver JAR."""
    return _drivers_dir() / "duckdb_jdbc.jar"


def odbc_path() -> Path:
    """Return the path to the ODBC driver DLL (Windows)."""
    return _drivers_dir() / "duckdb_odbc.dll"


def odbc_installer_path() -> Path:
    """Return the path to the ODBC installer (Windows)."""
    return _drivers_dir() / "odbc_install.exe"


# ------------------------------------------------------------------
# Status checks
# ------------------------------------------------------------------
def drivers_status() -> dict:
    """Return a dict with the status of each driver."""
    return {
        "drivers_dir": str(_drivers_dir()),
        "jdbc": {
            "installed": jdbc_path().exists(),
            "path": str(jdbc_path()),
            "size_mb": (jdbc_path().stat().st_size / 1024 / 1024
                        if jdbc_path().exists() else 0),
        },
        "odbc": {
            "installed": odbc_path().exists() if OS_NAME == "windows" else False,
            "path": str(odbc_path()),
            "note": "Windows only" if OS_NAME != "windows" else "",
        },
    }


def print_drivers_status() -> None:
    """Print a summary of installed BI drivers."""
    status = drivers_status()

    print()
    print("=" * 66)
    print("  BI Drivers Status")
    print("=" * 66)
    print(f"  Drivers dir: {status['drivers_dir']}")
    print()

    jdbc = status["jdbc"]
    mark = "[ok]" if jdbc["installed"] else "[XX]"
    print(f"  {mark} JDBC: {jdbc['path']}")
    if jdbc["installed"]:
        print(f"        Size: {jdbc['size_mb']:.1f} MB")

    odbc = status["odbc"]
    if OS_NAME == "windows":
        mark = "[ok]" if odbc["installed"] else "[XX]"
        print(f"  {mark} ODBC: {odbc['path']}")
    else:
        print(f"  [--] ODBC: {odbc['note']}")

    print()


# ------------------------------------------------------------------
# ODBC installation (Windows)
# ------------------------------------------------------------------
def install_odbc_driver() -> bool:
    """
    Install the DuckDB ODBC driver on Windows.

    Runs the bundled `odbc_install.exe` from the drivers folder.
    Requires Administrator privileges.
    """
    if OS_NAME != "windows":
        print("ODBC auto-install is only supported on Windows.")
        print("On Linux/macOS, build DuckDB ODBC from source:")
        print("  https://duckdb.org/docs/stable/api/odbc/overview")
        return False

    installer = odbc_installer_path()
    if not installer.exists():
        print(f"Installer not found: {installer}")
        print("Run 'python setup.py' to download it.")
        return False

    print(f"Running ODBC installer: {installer}")
    print("(You may see a UAC prompt - accept it)")

    try:
        r = subprocess.run([str(installer)], shell=True)
        if r.returncode == 0:
            print("  [ok] ODBC driver installed")
            return True
        print(f"  [!!] Installer returned code {r.returncode}")
        return False
    except Exception as exc:
        print(f"  [!!] Failed: {exc}")
        return False


# ------------------------------------------------------------------
# JDBC installation for specific tools
# ------------------------------------------------------------------
def copy_jdbc_to_tableau() -> bool:
    """Copy the JDBC driver to Tableau's driver folder."""
    jar = jdbc_path()
    if not jar.exists():
        print(f"JDBC driver not found: {jar}")
        print("Run 'python setup.py' to download it.")
        return False

    # Find Tableau install folder
    if OS_NAME == "windows":
        base = Path("C:/Program Files/Tableau")
        if not base.exists():
            print("Tableau not found at C:/Program Files/Tableau")
            return False
        candidates = sorted(base.glob("20*"), reverse=True)
        if not candidates:
            print("No Tableau version folder found")
            return False
        target_dir = candidates[0] / "Drivers"
    else:
        target_dir = Path.home() / "Library" / "Tableau" / "Drivers"

    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / jar.name

    import shutil
    shutil.copy2(jar, target)
    print(f"  [ok] Copied to {target}")
    print("  Restart Tableau for the change to take effect.")
    return True


def copy_jdbc_to_qlik() -> bool:
    """Copy the JDBC driver to Qlik Sense's driver folder."""
    jar = jdbc_path()
    if not jar.exists():
        print(f"JDBC driver not found: {jar}")
        print("Run 'python setup.py' to download it.")
        return False

    if OS_NAME == "windows":
        target_dir = Path("C:/Program Files/Common Files/QlikTech/Custom Data")
    else:
        target_dir = Path("/opt/qlik/customdata")

    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / jar.name

    import shutil
    shutil.copy2(jar, target)
    print(f"  [ok] Copied to {target}")
    print("  Restart Qlik Sense for the change to take effect.")
    return True


# ------------------------------------------------------------------
# Manual path info
# ------------------------------------------------------------------
def print_connection_info(db_path: str = "my_database.duckdb") -> None:
    """Print connection strings for common BI tools."""
    jdbc = jdbc_path()
    abs_db = (ROOT_DIR / db_path).resolve()

    print()
    print("=" * 66)
    print("  BI Tool Connection Info")
    print("=" * 66)
    print()
    print(f"  DuckDB file: {abs_db}")
    print(f"  JDBC driver: {jdbc}")
    print()

    print("  ── Tableau (JDBC) ────────────────────────────────────")
    print(f"     Driver path: {jdbc}")
    print(f"     JDBC URL:    jdbc:duckdb:{abs_db}")
    print(f"     Dialect:     PostgreSQL")
    print()

    print("  ── Power BI (ODBC) ───────────────────────────────────")
    if OS_NAME == "windows":
        print(f"     1. Run installer: {odbc_installer_path()}")
        print(f"     2. Create System DSN pointing to: {abs_db}")
        print(f"     3. In Power BI: Get Data -> ODBC -> DSN")
    else:
        print("     ODBC only supported on Windows in this toolkit")
    print()

    print("  ── Qlik Sense (ODBC or JDBC) ─────────────────────────")
    print(f"     ODBC DSN or JDBC driver path")
    print()


# ------------------------------------------------------------------
# ODBC DSN creation helper (Windows)
# ------------------------------------------------------------------
def create_odbc_dsn(db_path: str,
                    dsn_name: str = "DuckDB_Data") -> bool:
    """
    Create a System DSN for the given DuckDB file on Windows.

    Requires Administrator privileges.
    """
    if OS_NAME != "windows":
        print("DSN creation is Windows-only.")
        return False

    abs_db = (ROOT_DIR / db_path).resolve()
    if not abs_db.exists():
        print(f"Database not found: {abs_db}")
        return False

    print(f"Creating System DSN: {dsn_name}")
    print(f"  Database: {abs_db}")
    print()
    print("  Open ODBC Data Sources (64-bit) manually and:")
    print(f"    1. System DSN -> Add -> DuckDB Driver")
    print(f"    2. Name: {dsn_name}")
    print(f"    3. Database: {abs_db}")
    print()
    print("  Or use PowerShell as Administrator:")
    print()
    print(f'    Add-OdbcDsn -Name "{dsn_name}" -DriverName "DuckDB Driver" '
          f'-DsnType "System" -Platform "64-bit" '
          f'-SetPropertyValue @("Database={abs_db}")')
    return True
