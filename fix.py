#!/usr/bin/env python3
"""Fix JDBC URL and extension skip messages in setup.py."""

from pathlib import Path

ROOT = Path(__file__).parent.resolve()
SETUP = ROOT / "setup.py"

JDBC_VERSION = "1.3.1.0"


def main():
    if not SETUP.exists():
        print("setup.py not found")
        return

    text = SETUP.read_text(encoding="utf-8")

    # Fix 1: Replace JDBC version
    old_version = '"duckdb_jdbc/1.4.1/duckdb_jdbc-1.4.1.jar"'
    new_version = f'"duckdb_jdbc/{JDBC_VERSION}/duckdb_jdbc-{JDBC_VERSION}.jar"'

    if old_version in text:
        text = text.replace(old_version, new_version)
        print(f"  [ok] JDBC version changed to {JDBC_VERSION}")
    elif JDBC_VERSION in text:
        print(f"  [ok] JDBC already at {JDBC_VERSION}")
    else:
        print("  [!!] Could not find JDBC version line")
        print("  Please check line 745 manually.")

    # Fix 2: Replace the extension skip warning with a friendlier version
    old_warn = '            warn(name + "  (" + repo + ") - skipped")'
    new_warn = '''            if name in ("whisper", "cassandra") and OS == "windows":
                info(f"{name} ({repo}) - not available for Windows (this is fine)")
                if name == "whisper":
                    info("  Use the openai-whisper Python package instead")
                elif name == "cassandra":
                    info("  Use ODBC or a Python Cassandra driver")
            else:
                warn(name + "  (" + repo + ") - skipped")'''

    if old_warn in text:
        text = text.replace(old_warn, new_warn)
        print("  [ok] Added friendly messages for skipped extensions")
    elif "not available for Windows" in text:
        print("  [ok] Extension messages already updated")
    else:
        print("  [!!] Could not find extension warning line")
        print("  Please check line 657 manually.")

    SETUP.write_text(text, encoding="utf-8")
    print()
    print("  Done.")
    print()
    print("  Next:")
    print("    rm -rf runtime/duckdb/drivers")
    print("    python setup.py")


if __name__ == "__main__":
    main()