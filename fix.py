#!/usr/bin/env python3
"""
Replace em-dash (; ) with semicolon (; ) across the project.

Skips:
- binary files (models, images, duckdb files)
- installed packages (runtime/)
- git internals (.git/)
- cache folders (__pycache__, .ipynb_checkpoints)
"""

from pathlib import Path

ROOT = Path(__file__).parent.resolve()

# Only these extensions will be processed
TEXT_EXTENSIONS = {
    ".md", ".py", ".html", ".htm", ".css", ".js",
    ".yaml", ".yml", ".json", ".txt", ".sh", ".bat",
    ".cfg", ".toml", ".ini", ".csv", ".env",
}

# Folders to skip
SKIP_DIRS = {
    "runtime",
    ".git",
    "__pycache__",
    ".ipynb_checkpoints",
    ".venv",
    "venv",
    "node_modules",
    "python_portable",
    "duckdb_portable",
    "offline",
    ".vscode",
    ".idea",
}

EM_DASH = "\u2014"      # ;
EN_DASH = "\u2013"      # ;
SEMICOLON = "; "


def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    return False


def main() -> None:
    print()
    print("=" * 60)
    print("  Replacing em-dash (; ) with semicolon (; )")
    print("=" * 60)
    print()

    changed = []
    skipped = 0

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            skipped += 1
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            skipped += 1
            continue

        if EM_DASH not in text and EN_DASH not in text:
            continue

        # Count occurrences
        n_em = text.count(EM_DASH)
        n_en = text.count(EN_DASH)

        # Replace both em-dash and en-dash
        new_text = text.replace(EM_DASH, SEMICOLON)
        new_text = new_text.replace(EN_DASH, SEMICOLON)

        # Add space after semicolon if it was between words
        # (avoid "word; word" - make it "word; word")
        import re
        new_text = re.sub(r"; (\S)", r"; \1", new_text)

        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            rel = path.relative_to(ROOT)
            changed.append((rel, n_em + n_en))
            print(f"  [ok] {rel} ({n_em + n_en} replaced)")

    print()
    print("=" * 60)
    print(f"  Done. {len(changed)} files modified.")
    print(f"  {skipped} non-text files skipped.")
    print("=" * 60)
    print()

    if changed:
        print("  Next:")
        print("    git add .")
        print('    git commit -m "style: replace em-dash with semicolon"')
        print("    git push")
        print()


if __name__ == "__main__":
    main()