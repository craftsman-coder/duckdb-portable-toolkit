#!/usr/bin/env python3
"""
MCP server for the DuckDB Toolkit.

Exposes to the AI:
  - read-only SQL on DuckDB
  - list of tables and their schemas
  - business context (Markdown)
  - environment manifest (installed packages + extensions)
  - capabilities (what the AI can do)

Works fully offline over stdio.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Resource

import duckdb

app = Server("duckdb-portable-toolkit")

ROOT = Path(__file__).parent.parent.resolve()
RUNTIME = ROOT / "runtime"
MCP_DIR = ROOT / "mcp"

# Load config if available
def _load_cfg() -> dict:
    cfg_file = ROOT / "config.yaml"
    if not cfg_file.exists():
        return {}
    try:
        import yaml
        with open(cfg_file, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        return {}


CONFIG = _load_cfg()
MCP_CFG = CONFIG.get("mcp", {})
DB_PATH = MCP_CFG.get("db_path", ":memory:")
READ_ONLY = MCP_CFG.get("read_only", True)


# ------------------------------------------------------------------
# File loaders
# ------------------------------------------------------------------
def _read_file(path: Path, default: str = "") -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return default


def business_context() -> str:
    return _read_file(
        MCP_DIR / "context" / "business.md",
        "# Business Context\n\n_No business.md file found._",
    )


def environment_manifest() -> str:
    """Return the auto-generated manifest. Generate it if missing."""
    manifest = RUNTIME / "manifest.md"
    if not manifest.exists():
        try:
            from mcp import manifest_generator
            manifest_generator.main()
        except Exception as exc:
            return f"# Manifest\n\n_Could not generate: {exc}_"
    return _read_file(manifest, "# Manifest\n\n_Empty._")


def capabilities() -> str:
    return _read_file(
        MCP_DIR / "capabilities.md",
        "# Capabilities\n\n_No capabilities.md file found._",
    )


# ------------------------------------------------------------------
# DuckDB
# ------------------------------------------------------------------
def get_connection():
    conn = duckdb.connect(DB_PATH, read_only=READ_ONLY)
    ext = RUNTIME / "duckdb" / "extensions"
    conn.execute(f"SET extension_directory='{ext}'")
    return conn


# ------------------------------------------------------------------
# Tools
# ------------------------------------------------------------------
@app.list_tools()
async def list_tools():
    return [
        {
            "name": "query",
            "description": (
                "Run a read-only SQL SELECT query against DuckDB. "
                "Only SELECT statements are allowed."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "The SELECT SQL query"}
                },
                "required": ["sql"],
            },
        },
        {
            "name": "list_tables",
            "description": "List all tables in the DuckDB database.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "describe",
            "description": "Get column information for a specific table.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "table": {"type": "string", "description": "Table name"}
                },
                "required": ["table"],
            },
        },
        {
            "name": "business_context",
            "description": (
                "Return the business context: table descriptions, business "
                "rules, and common metrics. Call this before writing complex "
                "queries."
            ),
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "environment_manifest",
            "description": (
                "Return the environment manifest: all installed Python "
                "packages with versions and all DuckDB extensions. Call "
                "this to know what tools are available before suggesting "
                "code."
            ),
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "capabilities",
            "description": (
                "Return the list of capabilities: what the AI can do in "
                "this environment, style guide, and available toolkit "
                "helpers. Call this once per session."
            ),
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "query":
            sql = arguments.get("sql", "").strip()
            if not sql.upper().startswith("SELECT"):
                return [TextContent(type="text",
                                    text="Error: Only SELECT queries are allowed.",
                                    isError=True)]
            conn = get_connection()
            df = conn.execute(sql).fetchdf()
            conn.close()
            return [TextContent(type="text",
                                text=df.to_json(orient="records", indent=2))]

        if name == "list_tables":
            conn = get_connection()
            df = conn.execute(
                "SELECT table_schema, table_name FROM information_schema.tables "
                "WHERE table_schema NOT IN ('information_schema', 'pg_catalog') "
                "ORDER BY 1, 2"
            ).fetchdf()
            conn.close()
            return [TextContent(type="text",
                                text=df.to_json(orient="records", indent=2))]

        if name == "describe":
            table = arguments.get("table", "").strip()
            if not table:
                return [TextContent(type="text", text="Error: table name required",
                                    isError=True)]
            conn = get_connection()
            df = conn.execute(f"DESCRIBE {table}").fetchdf()
            conn.close()
            return [TextContent(type="text",
                                text=df.to_json(orient="records", indent=2))]

        if name == "business_context":
            return [TextContent(type="text", text=business_context())]

        if name == "environment_manifest":
            return [TextContent(type="text", text=environment_manifest())]

        if name == "capabilities":
            return [TextContent(type="text", text=capabilities())]

        return [TextContent(type="text", text=f"Unknown tool: {name}",
                            isError=True)]

    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {exc}", isError=True)]


# ------------------------------------------------------------------
# Resources
# ------------------------------------------------------------------
@app.list_resources()
async def list_resources():
    return [
        Resource(uri="duckdb://schema", name="Database Schema",
                 description="Tables and columns in the DuckDB database",
                 mimeType="text/plain"),
        Resource(uri="duckdb://business", name="Business Context",
                 description="Business rules and table descriptions",
                 mimeType="text/markdown"),
        Resource(uri="duckdb://manifest", name="Environment Manifest",
                 description="Installed packages and DuckDB extensions",
                 mimeType="text/markdown"),
        Resource(uri="duckdb://capabilities", name="AI Capabilities",
                 description="What the AI can do in this environment",
                 mimeType="text/markdown"),
    ]


@app.read_resource()
async def read_resource(uri: str):
    u = str(uri)
    if u == "duckdb://schema":
        try:
            conn = get_connection()
            tables = conn.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema NOT IN ('information_schema', 'pg_catalog')"
            ).fetchdf()
            lines = ["# Database Schema\n"]
            for t in tables["table_name"]:
                lines.append(f"\n## {t}\n")
                cols = conn.execute(f"DESCRIBE {t}").fetchdf()
                for _, row in cols.iterrows():
                    lines.append(f"- {row['column_name']} ({row['column_type']})")
            conn.close()
            return "\n".join(lines)
        except Exception as exc:
            return f"Error: {exc}"

    if u == "duckdb://business":
        return business_context()
    if u == "duckdb://manifest":
        return environment_manifest()
    if u == "duckdb://capabilities":
        return capabilities()

    return f"Unknown resource: {uri}"


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())