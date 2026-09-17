#!/usr/bin/env python3
"""Fix the DuckDB extensions check in verify.py."""

from pathlib import Path
import re

ROOT = Path(__file__).parent.resolve()
VERIFY = ROOT / "verify.py"


# New function that recursively counts extensions and uses proper load
NEW_FUNC = '''@check("DuckDB extensions")
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
'''


def main() -> None:
    if not VERIFY.exists():
        print("verify.py not found")
        return

    text = VERIFY.read_text(encoding="utf-8")

    # Find the old DuckDB extensions check function
    pattern = re.compile(
        r'@check\("DuckDB extensions"\)\n'
        r'def _c\d+\(\):\n'
        r'(?:.*\n)*?'
        r'    return r\.returncode == 0, f"\{r\.stdout\.strip\(\)\} extensions"\n',
        re.MULTILINE,
    )

    if pattern.search(text):
        text = pattern.sub(NEW_FUNC, text, count=1)
        VERIFY.write_text(text, encoding="utf-8")
        print("  [ok] DuckDB extensions check updated (recursive)")
    else:
        print("  [!!] could not find the extensions check")
        print("       Look for '@check(\"DuckDB extensions\")' in verify.py")
        print("       and replace that whole function with the new one.")


if __name__ == "__main__":
    main()