"""UI helpers for DuckDB, Streamlit, and llama.cpp."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

from toolkit.config import load

OS_NAME = "windows" if os.name == "nt" else "linux"
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

_streamlit_procs: list = []


def _docker_available() -> bool:
    return shutil.which("docker") is not None


def start_duck_ui(port: int = 5522,
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
        print("duck-ui already running at http://localhost:" + str(port))
        return "http://localhost:" + str(port)

    cmd = [
        "docker", "run", "-d", "--rm",
        "--name", "duck-ui",
        "-p", str(port) + ":5522",
        image,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Failed to start duck-ui: " + result.stderr[:300])
        return None
    time.sleep(2)
    url = "http://localhost:" + str(port)
    print("duck-ui is running at " + url)
    return url


def stop_duck_ui() -> None:
    """Stop the duck-ui container."""
    subprocess.run(["docker", "stop", "duck-ui"],
                   capture_output=True, text=True)
    print("Stopped duck-ui.")


def _streamlit_exe() -> Path:
    if OS_NAME == "windows":
        return PROJECT_ROOT / "runtime" / "venv" / "Scripts" / "streamlit.exe"
    return PROJECT_ROOT / "runtime" / "venv" / "bin" / "streamlit"


def start_streamlit(script_path: str,
                    port: int = 8501) -> Optional[str]:
    """Launch a Streamlit dashboard in the background."""
    cfg = load()
    runtime_cfg = cfg.get("runtime", {})
    port = port or runtime_cfg.get("streamlit_port", 8501)

    exe = _streamlit_exe()
    if not exe.exists():
        print("Streamlit not found at " + str(exe))
        return None

    script = PROJECT_ROOT / script_path
    if not script.exists():
        print("Script not found: " + str(script))
        return None

    cmd = [
        str(exe), "run", str(script),
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]

    print("Starting Streamlit on port " + str(port))
    proc = subprocess.Popen(
        cmd,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _streamlit_procs.append(proc)
    time.sleep(4)

    url = "http://localhost:" + str(port)
    print("Streamlit running at " + url)
    return url


def stop_streamlit() -> None:
    """Stop all Streamlit processes started in this session."""
    for proc in _streamlit_procs:
        try:
            proc.terminate()
        except Exception:
            pass
    _streamlit_procs.clear()
    print("Stopped all Streamlit processes.")


def start_llama_cpp(port: int = 8080) -> Optional[str]:
    """Start the llama.cpp server in the background."""
    cfg = load()
    ai_cfg = cfg.get("ai", {})
    if not ai_cfg.get("enabled", False):
        print("AI assistant disabled in config.yaml")
        return None

    bin_dir = PROJECT_ROOT / ai_cfg.get("bin_dir", "runtime/llama.cpp")
    exe_name = "llama-server.exe" if OS_NAME == "windows" else "llama-server"
    server_exe = bin_dir / exe_name

    if not server_exe.exists():
        print("llama-server not found at " + str(server_exe))
        print("Run: python setup.py")
        return None

    model_cfg = ai_cfg.get("model", {})
    model_dir = PROJECT_ROOT / model_cfg.get("dir", "runtime/models")
    filename = model_cfg.get("filename",
                             "qwen2.5-1.5b-instruct-q4_k_m.gguf")
    model_path = model_dir / filename

    if not model_path.exists():
        print("Model not found at " + str(model_path))
        print("Run: python setup.py")
        return None

    port = port or ai_cfg.get("port", 8080)
    server_cfg = ai_cfg.get("server", {})

    cmd = [
        str(server_exe),
        "-m", str(model_path),
        "--host", "0.0.0.0",
        "--port", str(port),
        "-t", str(server_cfg.get("threads", 4)),
        "-c", str(server_cfg.get("ctx_size", 2048)),
        "-b", str(server_cfg.get("batch_size", 512)),
        "-ngl", str(server_cfg.get("n_gpu_layers", 0)),
    ]

    print("Starting llama.cpp server on port " + str(port))
    subprocess.Popen(cmd,
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    time.sleep(3)

    url = "http://localhost:" + str(port)
    print("llama.cpp server running at " + url)
    return url


def stop_llama_cpp() -> None:
    """Stop the llama.cpp server."""
    if OS_NAME == "windows":
        subprocess.run(["taskkill", "/F", "/IM", "llama-server.exe"],
                       capture_output=True, text=True)
    else:
        subprocess.run(["pkill", "-f", "llama-server"],
                       capture_output=True, text=True)
    print("Stopped llama.cpp server.")


def start_all_dashboards() -> dict:
    """Start every dashboards/*.py on sequential ports."""
    dash_dir = PROJECT_ROOT / "dashboards"
    if not dash_dir.exists():
        print("No dashboards/ folder found.")
        return {}

    scripts = sorted(
        p for p in dash_dir.glob("*.py") if not p.name.startswith("_")
    )
    if not scripts:
        print("No dashboard scripts found.")
        return {}

    result = {}
    port = 8501
    for s in scripts:
        rel = s.relative_to(PROJECT_ROOT).as_posix()
        url = start_streamlit(rel, port=port)
        if url:
            result[rel] = url
            port += 1
    return result
