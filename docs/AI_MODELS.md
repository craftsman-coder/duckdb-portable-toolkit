# AI Models with llama.cpp

The toolkit uses **llama.cpp** as its local AI engine. It's fully
portable, lightweight (~89 MB binary), and runs on CPU without a GPU.

The default model is **Qwen2.5-1.5B-Instruct** (Q4_K_M quantized, ~1 GB).

## Why llama.cpp over Ollama?

| Feature | llama.cpp | Ollama |
|---|---|---|
| Binary size | ~89 MB | ~680 MB |
| Startup time | 1-2 sec | 5-10 sec |
| RAM usage | ~100 MB | ~200+ MB |
| Portable | Yes | No |
| No background service | Yes | No |
| OpenAI-compatible API | Yes | Partial |

## Available models

In a Jupyter cell:

```python
from toolkit.maintenance import list_ai_models
list_ai_models()
```

Output:

```text
Name                     Size     Notes
------------------------------------------------------------------
qwen2.5-1.5b           1.0 GB   Fast, good for CPU. Recommended default.
qwen2.5-3b             2.0 GB   Better quality, needs 8 GB RAM.
qwen2.5-7b             4.5 GB   Best quality on CPU, needs 16 GB RAM.
qwen2.5-coder-1.5b     1.0 GB   Optimized for code. Very fast.
qwen2.5-coder-7b       4.5 GB   Best code model, needs 16 GB RAM.
tinyllama-1.1b         0.7 GB   Ultra-light, works on any CPU.
```

## Switch to a different model

```python
from toolkit.maintenance import change_ai_model
change_ai_model("qwen2.5-7b")
```

This will:

1. Download the GGUF file to `runtime/models/`
2. Update `config.yaml` with the new filename and URL
3. Print instructions to restart the server

Then restart the server:

```python
from toolkit.ui import stop_llama_cpp, start_llama_cpp
stop_llama_cpp()
start_llama_cpp()
```

## Download only (without switching)

```python
from toolkit.maintenance import download_ai_model
download_ai_model("qwen2.5-coder-7b")
```

Useful if you want the model available for later but keep the current
one active for now.

## Use a custom GGUF model

1. Copy the file to `runtime/models/`:

   ```text
   runtime/models/my-model.gguf
   ```

2. Edit `config.yaml`:

   ```yaml
   ai:
     model:
       dir: "runtime/models"
       filename: "my-model.gguf"
       download_url: ""
   ```

3. Restart the server.

## GPU acceleration

Set the number of layers offloaded to GPU in `config.yaml`:

```yaml
ai:
  server:
    n_gpu_layers: 999    # 0 = CPU only; 999 = all layers on GPU
```

Restart the server after changing this.

### Requirements by GPU vendor

| GPU | Requirements |
|---|---|
| NVIDIA | CUDA 12.x, latest driver |
| AMD | ROCm 5.6+ |
| Apple Silicon | macOS 13+ (Metal built in) |
| Intel Arc | oneAPI |

### Verify GPU is used

**NVIDIA:**

```bash
nvidia-smi
# Look for llama-server in the process list
```

**AMD:**

```bash
rocm-smi
```

For CPU-only setups (the default), leave `n_gpu_layers: 0`.

## Performance on CPU

| Model | Speed | RAM needed |
|---|---|---|
| tinyllama-1.1b | ~25 tok/s | 2 GB |
| qwen2.5-1.5b | ~15 tok/s | 3 GB |
| qwen2.5-3b | ~8 tok/s | 6 GB |
| qwen2.5-7b | ~3 tok/s | 12 GB |

### Tips to speed up CPU inference

1. Increase threads in `config.yaml` (match CPU cores)
2. Reduce `ctx_size` if you don't need long context
3. Close other applications to free RAM

## Server options

```yaml
ai:
  server:
    threads: 4          # CPU threads
    ctx_size: 2048      # context window in tokens
    batch_size: 512     # prompt batch size
    n_gpu_layers: 0     # 0 = CPU only
```

Restart the server after any change.

## Managing the server

### Start

```python
from toolkit.ui import start_llama_cpp
start_llama_cpp()
# -> http://localhost:8080
```

### Stop

```python
from toolkit.ui import stop_llama_cpp
stop_llama_cpp()
```

### Check status

```python
import urllib.request
try:
    urllib.request.urlopen("http://localhost:8080/v1/models", timeout=2)
    print("Server is running")
except Exception:
    print("Server is not running")
```

## Connect Jupyter AI

In JupyterLab, open **Settings -> Settings Editor -> Jupyter AI**:

- **Provider:** `Generic (OpenAI-compatible)`
- **Base URL:** `http://localhost:8080/v1`
- **API key:** (leave empty)
- **Model:** the filename without `.gguf`

Then open the chat panel (left sidebar) and start asking questions.

## Command-line usage

```bash
# Windows
runtime\llama.cpp\llama-server.exe ^
    -m runtime\models\qwen2.5-1.5b-instruct-q4_k_m.gguf ^
    --port 8080

# Linux / macOS
runtime/llama.cpp/llama-server \
    -m runtime/models/qwen2.5-1.5b-instruct-q4_k_m.gguf \
    --port 8080
```

## Troubleshooting

### "llama-server not found"

Run `python setup.py` to download llama.cpp.

### "Model not found"

Run `python setup.py` or:

```python
from toolkit.maintenance import download_ai_model
download_ai_model("qwen2.5-1.5b")
```

### Server starts but Jupyter AI cannot connect

- Verify the URL: `http://localhost:8080/v1`
- Check that port 8080 is not used by another process

### Slow responses

- Use a smaller model
- Increase `threads` in `config.yaml`
- Reduce `ctx_size`

### Out of memory

- Use a smaller model
- Reduce `ctx_size` and `batch_size`

### GPU not detected

- Verify driver: `nvidia-smi` (NVIDIA) or `rocm-smi` (AMD)
- Restart the server after installing drivers

## Next Steps

- [RAG with your documents](RAG.md)
- [MCP Server for AI](../mcp/capabilities.md)
- [Offline installation](OFFLINE_INSTALL.md)
