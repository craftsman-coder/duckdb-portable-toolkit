#!/usr/bin/env python3
"""
Remove 'Portable' from the title everywhere.
Keep the word 'portable' in descriptions where it makes sense.
"""

from pathlib import Path

ROOT = Path(__file__).parent.resolve()

TEXT_EXTENSIONS = {".md", ".py", ".html", ".yaml", ".yml", ".txt", ".json"}

SKIP_DIRS = {
    "runtime", ".git", "__pycache__", ".ipynb_checkpoints",
    "node_modules", "offline",
}

# Patterns to replace (order matters - longer first)
REPLACEMENTS = [
    # Titles with "Portable" (capital P)
    ("DuckDB Toolkit", "DuckDB Toolkit"),
    ("DuckDB Toolkit", "DuckDB Toolkit"),
    # Windows-specific
    ("DuckDB Toolkit -", "DuckDB Toolkit -"),
    ("DuckDB Toolkit -", "DuckDB Toolkit -"),
    # Launchers output
    ("DuckDB Toolkit\n", "DuckDB Toolkit\n"),
    # Paths (careful - don't touch real paths)
    # Do NOT replace "duckdb-portable-toolkit" (repo name)
]


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def main() -> None:
    print()
    print("=" * 60)
    print("  Removing 'Portable' from title")
    print("=" * 60)
    print()

    changed = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        new_text = text
        for old, new in REPLACEMENTS:
            if old in new_text:
                new_text = new_text.replace(old, new)

        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            rel = path.relative_to(ROOT)
            changed.append(rel)
            print(f"  [ok] {rel}")

    print()
    print("=" * 60)
    print(f"  Done. {len(changed)} files modified.")
    print("=" * 60)
    print()

    if changed:
        print("  Next:")
        print("    1. Update the GitHub repo name (optional):")
        print("       Settings -> Repository name -> duckdb-toolkit")
        print()
        print("    2. Update the About description:")
        print("       DuckDB Toolkit; no install, no root, no venv.")
        print()
        print("    3. Commit and push:")
        print("       git add .")
        print('       git commit -m "style: drop Portable from title"')
        print("       git push")
        print()


if __name__ == "__main__":
    main()