# %% [markdown]
# # 20 - Local AI Assistant
#
# Uses the llama.cpp server with Qwen 1.5B.
# The server runs locally at http://localhost:8080

# %%
# Start the server (if not already running)
from toolkit.ui import start_llama_cpp

url = start_llama_cpp()
print(f"Server: {url}")

# %%
# Simple chat helper
import json
import urllib.request


def ask(question: str, system: str = "") -> str:
    """Send a question to the local AI and return the answer."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": question})

    payload = json.dumps({
        "model": "qwen2.5-1.5b-instruct",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512,
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://localhost:8080/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


# %%
# Ask a simple question
answer = ask("What is a DuckDB? Answer in one sentence.")
print(answer)

# %%
# Ask for code
code = ask(
    "Write a Python function that reads a Parquet file "
    "and returns the top 5 rows by a column named 'amount'. "
    "Use pandas. Only output the code.",
    system="You are a Python expert. Reply with code only.",
)
print(code)

# %%
# Ask about your data
context = """
Table: sales
Columns:
  - sale_date (DATE)
  - amount (DOUBLE)   -- in Iranian Rials
  - customer_id (INT)
  - status (VARCHAR)  -- 'active', 'cancelled', 'refund'
"""

sql = ask(
    f"Given this schema:\n{context}\n\n"
    "Write a SQL query to get monthly revenue "
    "for active sales only. Output SQL only.",
    system="You are a DuckDB SQL expert.",
)
print(sql)

# %%
# Interactive mode (uncomment to use)
# while True:
#     q = input("You: ")
#     if q.lower() in ("exit", "quit"):
#         break
#     print("AI:", ask(q))
#     print()

# %%
# Stop the server when done
from toolkit.ui import stop_llama_cpp
stop_llama_cpp()