# Manifest Generator

The `mcp/manifest_generator.py` script creates `runtime/manifest.md`:
a snapshot of everything installed in your environment. The AI reads
this through the MCP server to know what tools are available.

## When to Run

- **After `setup.py`**; automatic (no action needed)
- **After installing new packages**; manually
- **After installing new DuckDB extensions**; manually
- **Before starting work with AI**; for safety

## How to Run

### Windows (PowerShell or CMD)

```cmd
runtime\python\python.exe mcp\manifest_generator.py
```

### Linux / macOS / Git Bash

```bash
runtime/python/bin/python3 mcp/manifest_generator.py
```

Note: in Git Bash on Windows, use forward slashes:

```bash
runtime/python/python.exe mcp/manifest_generator.py
```

### From Jupyter

In any notebook cell:

```python
%run mcp/manifest_generator.py
```

Or:

```python
import importlib
import mcp.manifest_generator as mg
importlib.reload(mg)
mg.main()
```

## Output

The script writes `runtime/manifest.md`:

```markdown
# Environment Manifest

Generated: 2026-09-18T11:30:22
OS: Windows 11
Architecture: AMD64

## Python packages

| Package | Version |
|---|---|
| duckdb | 1.5.5 |
| pandas | 2.3.3 |
| numpy | 2.3.5 |
| jupyterlab | 4.6.3 |

## DuckDB

- Version: **1.5.5**

## DuckDB extensions

| Extension | Description |
|---|---|
| iceberg | Iceberg table support |
| delta | Delta Lake support |
| oracle_scanner | Query Oracle databases |

## Toolkit helper modules

- `toolkit.config`
- `toolkit.io_helpers`
- `toolkit.jobs`
- `toolkit.lakehouse`
- `toolkit.maintenance`
- `toolkit.ml`
- `toolkit.parallel`
- `toolkit.rag`
- `toolkit.transcribe`
- `toolkit.ui`
```

## How the AI Uses It

The MCP server exposes the manifest as a tool:

```python
environment_manifest()
```

When the AI needs to know what's installed, it calls this tool and
receives the Markdown content. This prevents the AI from suggesting
packages that aren't installed.

**Example conversation:**

> **You:** Write a script to profile a DataFrame.
>
> **AI (thinking):** Let me check what's installed.
> → calls `environment_manifest()`
> → sees `ydata-profiling` in the list
> **AI:** Here's a script using ydata-profiling...

## Automating It

### Git hook (Linux / macOS)

Add to `.git/hooks/post-merge`:

```bash
#!/bin/sh
cd "$(git rev-parse --show-toplevel)"
runtime/python/bin/python3 mcp/manifest_generator.py
```

Make it executable:

```bash
chmod +x .git/hooks/post-merge
```

### Alias (any OS)

Add to `~/.bashrc` (Linux) or `~/.bash_profile`:

```bash
alias refresh-manifest='cd ~/duckdb-portable-toolkit && runtime/python/bin/python3 mcp/manifest_generator.py'
```

### From Python (in a notebook)

```python
from toolkit.maintenance import refresh_ai_docs
refresh_ai_docs()
```

This is the simplest option; call it after any install.

## What It Reads

The manifest generator inspects:

1. **Python packages**; via `pip list --format=json`
2. **DuckDB version**; by importing `duckdb` in the portable Python
3. **DuckDB extensions**; by querying `duckdb_extensions()`
4. **Toolkit modules**; by listing `toolkit/*.py`

## Troubleshooting

### "No packages found"

This means the manifest generator couldn't find the portable Python.
Check that `runtime/python/python.exe` (or `runtime/python/bin/python3`)
exists.

If you recently moved the project, the `.pth` file that registers the
toolkit path may be stale. Re-run:

```bash
python setup.py
```

### Manifest not updating

Check the modification time:

```bash
ls -la runtime/manifest.md      # Linux / macOS / Git Bash
dir runtime\manifest.md         # Windows
```

If it's old, the generator didn't run. Run it manually.

### AI doesn't see new packages

The MCP server reads `runtime/manifest.md` on every request. If it's
not updating, the file might be cached by the AI. Try:

1. Regenerate the manifest
2. Restart the MCP client (or JupyterLab)
3. Ask the AI to call `environment_manifest()` again

## Manual Editing

The manifest is auto-generated; **don't edit it by hand**. Any
changes will be overwritten the next time the generator runs.

If you want to add custom notes for the AI, edit
`mcp/capabilities.md` instead.

## Next Steps

- [AI Models](AI_MODELS.md)
- [MCP Capabilities](../mcp/capabilities.md)
- [RAG](RAG.md)
