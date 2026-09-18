# Retrieval-Augmented Generation (RAG)

Give your local AI access to your own documents: business rules, PDF
extracts, markdown notes, CSV headers, SQL schemas — anything in text
form. The AI will search this library before answering.

Everything runs **offline** after the embedding model is downloaded.

## How it works

1. **Chunk** documents into ~500-character pieces.
2. **Embed** each chunk with `sentence-transformers/all-MiniLM-L6-v2`
   (a 90 MB model that runs on CPU in milliseconds).
3. **Store** the embeddings in a DuckDB table with a VSS (vector) index.
4. **Search** with cosine similarity when the user asks a question.
5. **Inject** the top-k chunks into the AI prompt.

## 1. Prepare your documents

Create a folder, e.g. `data/docs/`:

```text
data/docs/
├── business_rules.md
├── schema_notes.md
├── glossary.md
└── policies/
    ├── returns.md
    └── refunds.md
```

Plain text, Markdown, reStructuredText, and JSON are supported.

## 2. Build the index

```python
from toolkit.rag import create_index

create_index(
    docs_dir="data/docs",
    table_name="my_knowledge",
    db_path="runtime/rag.duckdb",
)
```

The first run downloads the embedding model (~90 MB), then chunks,
embeds, and stores everything.

## 3. Search

```python
from toolkit.rag import search

results = search("How do refunds work?", table_name="my_knowledge", k=3)
for r in results:
    print(f"[{r['score']:.3f}] {r['source']}")
    print(r["text"][:200])
    print("---")
```

Each result has:

- `source` — the file it came from
- `text` — the chunk content
- `score` — cosine similarity (higher = more relevant)

## 4. Feed results to your AI

### Option A: Copy the prompt manually

```python
from toolkit.rag import build_prompt

prompt = build_prompt("How do refunds work?", table_name="my_knowledge", k=5)
print(prompt)
# Copy the printed prompt into your Jupyter AI chat panel
```

### Option B: Let the MCP server do it

Add a tool to `mcp/server.py` that calls `toolkit.rag.search`:

```python
@app.call_tool()
async def call_tool(name, arguments):
    ...
    if name == "rag_search":
        query = arguments.get("query", "")
        from toolkit.rag import search
        hits = search(query, table_name="my_knowledge", k=5)
        return [TextContent(type="text",
                            text=json.dumps(hits, indent=2, ensure_ascii=False))]
```

Now the AI can call `rag_search("...")` on its own.

### Option C: Jupyter AI inline

```text
Use this context to answer:

<context>
... (paste build_prompt output) ...
</context>

Question: How do refunds work?
```

## 5. Keep the index fresh

```python
from toolkit.rag import create_index
create_index("data/docs", table_name="my_knowledge")
```

It drops and rebuilds the table, so it's always up to date.

### Incremental update (advanced)

```python
import duckdb
from pathlib import Path
from toolkit.config import EXTENSIONS_DIR

con = duckdb.connect("runtime/rag.duckdb")
con.execute(f"SET extension_directory='{EXTENSIONS_DIR}'; LOAD vss;")

existing = set(row[0] for row in con.execute(
    "SELECT DISTINCT source FROM my_knowledge"
).fetchall())

current = set(
    str(p.relative_to("data/docs"))
    for p in Path("data/docs").rglob("*") if p.is_file()
)

new = current - existing
removed = existing - current
print("new:", new)
print("removed:", removed)
```

## 6. Tuning

### Chunk size

```python
create_index("data/docs", chunk_size=800, chunk_overlap=100)
```

- Larger chunks = more context per hit, fewer hits
- Smaller chunks = more precise, but might miss context

Recommended: **500-800 characters** for prose, **300** for code.

### Number of results

```python
search("...", k=10)   # more context
search("...", k=3)    # less noise
```

Recommended: **3-5**.

### Different embedding model

```python
create_index(
    "data/docs",
    model_name="sentence-transformers/all-mpnet-base-v2",
)
```

| Model | Size | Speed | Quality |
|---|---|---|---|
| all-MiniLM-L6-v2 | 90 MB | Fastest | Good |
| all-mpnet-base-v2 | 420 MB | Medium | Better |
| BAAI/bge-small-en-v1.5 | 130 MB | Fast | Very good |
| BAAI/bge-large-en-v1.5 | 1.3 GB | Slow | Best |

If you switch models, you must re-index.

## 7. Multilingual documents

For Persian, Arabic, or other non-English documents:

```python
create_index(
    "data/docs",
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
```

For mixed Persian + English, use `paraphrase-multilingual-MiniLM-L12-v2`
or `BAAI/bge-m3`.

## 8. Example end-to-end

```python
from toolkit.rag import create_index, search
from toolkit.ui import start_llama_cpp

# 1. Build the index once
create_index("mcp/context", table_name="business")
create_index("data/docs",     table_name="policies")

# 2. Start the AI
start_llama_cpp()

# 3. Ask a question
q = "What's our return policy for wholesale customers?"
ctx1 = search(q, table_name="business", k=3)
ctx2 = search(q, table_name="policies", k=3)

prompt = (
    "Answer using the context below:\n\n"
    + "\n\n".join(r["text"] for r in ctx1 + ctx2)
    + f"\n\nQuestion: {q}"
)
print(prompt)
# Paste into Jupyter AI chat
```

## 9. Troubleshooting

### "model not found"

The embedding model must be downloaded once (needs internet).
After that it's cached in `~/.cache/huggingface/`.

### "vss extension not found"

```python
from toolkit.maintenance import install_duckdb_extension
install_duckdb_extension("vss")
```

### Search returns garbage

- Documents may be too short or too long
- Try different `chunk_size`
- Check that the query language matches the documents

### Slow first query

The embedding model loads into RAM (~90 MB for MiniLM).
Subsequent queries are much faster.

## 10. What to put in your docs

**Good candidates:**

- Business rules and definitions
- Data dictionary / column meanings
- Team conventions (naming, style)
- SQL snippets that worked
- Frequently-asked questions from colleagues

**Avoid:**

- Large PDFs without conversion (use `pdfplumber` first)
- Binary files
- Highly dynamic data (put that in DuckDB tables, not RAG)

## Next Steps

- [Local AI with llama.cpp](AI_MODELS.md)
- [MCP Server for AI](../mcp/capabilities.md)
- [Offline installation](OFFLINE_INSTALL.md)
