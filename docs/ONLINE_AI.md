# Online AI Models

The toolkit ships with a local llama.cpp model. If you need a
bigger or more capable model, you can plug in an online
provider that exposes an **OpenAI-compatible API**.

## Supported providers

| Provider | Base URL | Models |
|---|---|---|
| **OpenRouter** | `https://openrouter.ai/api/v1` | 400+ models from many providers |
| **OpenAI** | `https://api.openai.com/v1` | GPT-4o, GPT-4o-mini, o1, ... |
| **Groq** | `https://api.groq.com/openai/v1` | Llama, Mixtral, Gemma (very fast) |
| **Together** | `https://api.together.xyz/v1` | Many open models |
| **DeepSeek** | `https://api.deepseek.com/v1` | DeepSeek Chat / Reasoner |

Any other provider with an OpenAI-compatible endpoint also works.

## Setup

### 1. Get an API key

For OpenRouter, create a key at:
https://openrouter.ai/settings/keys

### 2. Configure the toolkit

Edit `config.yaml`:

```yaml
online_ai:
  enabled: true
  provider: "openrouter"
  model: "openai/gpt-4o-mini"
  api_key: "sk-or-v1-..."
  base_url: "https://openrouter.ai/api/v1"
  max_tokens: 1024
  temperature: 0.7
```

### 3. Use it from Python

```python
from toolkit.online_ai import chat, chat_stream, list_providers

# Simple one-shot call
reply = chat("Explain DuckDB in one sentence")
print(reply)

# With a system prompt and a specific model
reply = chat(
    "Summarize this support ticket",
    system="You are a helpful assistant.",
    model="anthropic/claude-3.5-sonnet",
)

# Streaming
for chunk in chat_stream("Write a haiku about data"):
    print(chunk, end="")

# Browse built-in presets
print(list_providers())
```

## LiteLLM: 100+ providers

For providers that do not speak the OpenAI format directly,
use the LiteLLM helper:

```python
from toolkit.online_ai import litellm_chat

reply = litellm_chat(
    "Write a Python function to read Parquet",
    model="openrouter/qwen/qwen3-coder",
)
print(reply)
```

## Use from the MCP server

The MCP server exposes an `online_ai_chat` tool. The local AI
can call it to delegate hard questions to an online model.

Example conversation in Jupyter AI:

> **You:** This SQL is too complex for you. Ask the online model.
> **AI:** (calls `online_ai_chat` with the SQL and question)
> (returns the online model's answer)

## Environment variables

Instead of putting the key in `config.yaml`, you can export it:

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
export OPENAI_API_KEY="sk-..."
```

The client reads the key from `config.yaml` first, then from the
environment variable matching the provider.

## Security notes

- Never commit your API key. `config.yaml` is tracked by git;
  prefer the `OPENROUTER_API_KEY` environment variable.
- If you must put the key in a file, add `config.yaml` to
  `.gitignore` (or use `configs/secrets.sql` for a dedicated file).
- The online model can see any data you send in the prompt.
  Do not send confidential data unless your provider allows it.
