"""
UI helpers for DuckDB.

- start_duck_ui(): launches the duck-ui Docker container (offline web UI)
- stop_duck_ui(): stops it
- start_ollama(): ensures the Ollama server is running
"""

from __future__ import annotations

import subprocess
import shutil
import time
from typing import Optional

from toolkit.config import load


def _docker_available() -> bool:
    return shutil.which("docker") is not None


def start_duck_ui(port: int | None = None,
                  image: str = "ghcr.io/caioricciuti/duck-ui:latest"
                  ) -> Optional[str]:
    """Launch duck-ui in a Docker container. Returns the URL."""
    cfg = load()
    ui_cfg = cfg.get("duck_ui", {})
    if not ui_cfg.get("enabled", False):
        print("duck-ui is disabled in config.yaml")
        return None
    port = port or ui_cfg.get("port", 5522)

    if not _docker_available():
        print("Docker not found. Install Docker to use duck-ui.")
        return None

    check = subprocess.run(
        ["docker", "ps", "--filter", "name=duck-ui", "--format", "{{.Names}}"],
        capture_output=True, text=True,
    )
    if "duck-ui" in check.stdout:
        print(f"duck-ui already running at http://localhost:{port}")
        return f"http://localhost:{port}"

    cmd = ["docker", "run", "-d", "--rm",
           "--name", "duck-ui",
           "-p", f"{port}:5522", image]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to start duck-ui: {result.stderr[:300]}")
        return None
    time.sleep(2)
    url = f"http://localhost:{port}"
    print(f"duck-ui is running at {url}")
    return url


def stop_duck_ui() -> None:
    subprocess.run(["docker", "stop", "duck-ui"], capture_output=True, text=True)


def start_ollama(host: str | None = None) -> Optional[str]:
    """Ensure Ollama is running. Returns the host URL."""
    ollama = shutil.which("ollama")
    if not ollama:
        print("Ollama not found. Install from https://ollama.com/download")
        return None

    cfg = load()
    ai_cfg = cfg.get("ai", {})
    if not ai_cfg.get("enabled", False):
        print("AI assistant disabled in config.yaml")
        return None

    host = host or ai_cfg.get("ollama_host", "http://localhost:11434")

    import urllib.request
    try:
        urllib.request.urlopen(f"{host}/api/tags", timeout=2)
        print(f"Ollama is already running at {host}")
        return host
    except Exception:
        pass

    print("Starting Ollama server...")
    subprocess.Popen([ollama, "serve"],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    time.sleep(3)
    print(f"Ollama started at {host}")
    return host