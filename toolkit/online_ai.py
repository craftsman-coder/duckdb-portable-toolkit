"""
Online AI helpers.

Call remote models through OpenRouter, OpenAI, or any
OpenAI-compatible endpoint.

Works alongside the local llama.cpp model; switch per call.
"""

from __future__ import annotations

from typing import Any

from toolkit.config import load


# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
def _online_cfg() -> dict:
    """Read the 'online_ai' section of config.yaml."""
    return load().get("online_ai", {})


def online_ai_enabled() -> bool:
    """Return True if online AI is enabled in config."""
    return bool(_online_cfg().get("enabled", False))


# ------------------------------------------------------------------
# OpenAI-compatible client (works with OpenRouter, OpenAI, etc.)
# ------------------------------------------------------------------
def get_client(api_key: str | None = None,
               base_url: str | None = None):
    """
    Return an OpenAI client configured for the chosen provider.

    Reads defaults from config.yaml's 'online_ai' section.
    Pass api_key or base_url to override.
    """
    from openai import OpenAI

    cfg = _online_cfg()
    api_key = api_key or cfg.get("api_key", "")
    base_url = base_url or cfg.get("base_url", "https://openrouter.ai/api/v1")

    if not api_key:
        raise ValueError(
            "No API key found. Set 'online_ai.api_key' in config.yaml "
            "or pass api_key=..."
        )

    return OpenAI(api_key=api_key, base_url=base_url)


def chat(prompt: str,
         system: str | None = None,
         model: str | None = None,
         max_tokens: int | None = None,
         temperature: float | None = None,
         api_key: str | None = None,
         base_url: str | None = None) -> str:
    """
    Send a single message to an online model and return its reply.

    Parameters
    ----------
    prompt : str
        The user's message.
    system : str, optional
        System prompt.
    model : str, optional
        Model slug, e.g. 'openai/gpt-4o-mini' or 'anthropic/claude-3.5-sonnet'.
        Defaults to 'online_ai.model' in config.yaml.
    max_tokens, temperature : optional
        Override defaults from config.yaml.
    """
    cfg = _online_cfg()
    model = model or cfg.get("model", "openai/gpt-4o-mini")
    max_tokens = max_tokens or cfg.get("max_tokens", 1024)
    temperature = temperature if temperature is not None else cfg.get("temperature", 0.7)

    client = get_client(api_key=api_key, base_url=base_url)

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content


def chat_stream(prompt: str,
                system: str | None = None,
                model: str | None = None,
                api_key: str | None = None,
                base_url: str | None = None):
    """Stream a reply from an online model, yielding text chunks."""
    cfg = _online_cfg()
    model = model or cfg.get("model", "openai/gpt-4o-mini")

    client = get_client(api_key=api_key, base_url=base_url)

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


# ------------------------------------------------------------------
# LiteLLM (works with 100+ providers)
# ------------------------------------------------------------------
def litellm_chat(prompt: str,
                 model: str = "openrouter/openai/gpt-4o-mini",
                 api_key: str | None = None,
                 system: str | None = None,
                 **kwargs: Any) -> str:
    """
    Call any model via LiteLLM.

    Model format: '<provider>/<model>', e.g.:
      - 'openrouter/anthropic/claude-3.5-sonnet'
      - 'openai/gpt-4o'
      - 'ollama/llama3' (local)

    Requires the appropriate API key for the provider.
    """
    import os
    from litellm import completion

    if api_key:
        os.environ["OPENROUTER_API_KEY"] = api_key
    # LiteLLM also reads OPENROUTER_API_KEY, OPENAI_API_KEY, etc. from env

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = completion(model=model, messages=messages, **kwargs)
    return resp.choices[0].message.content


# ------------------------------------------------------------------
# Provider presets
# ------------------------------------------------------------------
PROVIDERS = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "env_key": "OPENROUTER_API_KEY",
        "docs": "https://openrouter.ai/docs",
        "models_url": "https://openrouter.ai/models",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "env_key": "OPENAI_API_KEY",
        "docs": "https://platform.openai.com/docs",
        "models_url": "https://platform.openai.com/docs/models",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "env_key": "GROQ_API_KEY",
        "docs": "https://console.groq.com/docs",
        "models_url": "https://console.groq.com/docs/models",
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "env_key": "TOGETHER_API_KEY",
        "docs": "https://docs.together.ai/",
        "models_url": "https://docs.together.ai/docs/inference-models",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "env_key": "DEEPSEEK_API_KEY",
        "docs": "https://api-docs.deepseek.com",
        "models_url": "https://api-docs.deepseek.com/quick_start/pricing",
    },
}


def list_providers() -> dict:
    """Return the built-in provider presets."""
    return PROVIDERS


def provider_help(name: str) -> dict:
    """Return docs and model list for a known provider."""
    return PROVIDERS.get(name.lower(), {})
