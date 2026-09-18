# Connecting to duck-ui

`duck-ui` is a fully offline web interface for DuckDB. It runs in a
Docker container and lets you explore databases, run SQL, and
visualize data in your browser.

## Why use duck-ui?

- Quick data exploration without writing code
- Full-featured SQL editor with syntax highlighting
- Built-in simple charts (bar, line, pie)
- Works fully offline
- Complements JupyterLab (which is better for scripting)

## Requirements

**Docker** installed and running.

### Install Docker

**Windows / macOS:**

Download Docker Desktop from
[https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
and run the installer.

**Linux (Debian / Ubuntu):**

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

**Linux (Fedora):**

```bash
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

### Verify Docker

```bash
docker --version
docker ps
```

## Starting duck-ui

### From JupyterLab (recommended)

```python
from toolkit.ui import start_duck_ui
url = start_duck_ui()
print(url)
```

Output:

```text
duck-ui is running at http://localhost:5522
http://localhost:5522
```

Then open `http://localhost:5522` in your browser.

### From a terminal

```bash
docker run -d --rm \
  --name duck-ui \
  -p 5522:5522 \
  ghcr.io/caioricciuti/duck-ui:latest
```

### Change the port

```python
from toolkit.ui import start_duck_ui
start_duck_ui(port=5523)
```

### Custom image version

```python
start_duck_ui(image="ghcr.io/caioricciuti/duck-ui:v1.2.0")
```

## Using duck-ui

### 1. Connect to a DuckDB database

In duck-ui, click **New Connection** and enter:

- **Database path:** `runtime/duckdb/your_db.duckdb`
  (or any `.duckdb` file in the project)
- **Read-only:** check this box for safety

### 2. Upload a Parquet or CSV file

Drag and drop a file into the interface, or use the file picker.

### 3. Run SQL

```sql
SELECT
    DATE_TRUNC('month', sale_date) AS month,
    SUM(amount) AS revenue
FROM sales
WHERE status = 'active'
GROUP BY 1
ORDER BY 1;
```

### 4. Save queries

Use the **Save** button to keep frequently-used queries for later.

## Stopping duck-ui

### From Python

```python
from toolkit.ui import stop_duck_ui
stop_duck_ui()
```

### From terminal

```bash
docker stop duck-ui
```

## Offline Operation

duck-ui works fully offline:

- The container image is pulled once (needs internet)
- After that, everything is local
- No data leaves your machine

**Verify offline operation:**

1. Start duck-ui
2. Disconnect from the internet
3. Open `http://localhost:5522` ; it should still work

## Persistent storage (optional)

```bash
docker run -d --rm \
  --name duck-ui \
  -p 5522:5522 \
  -v "$(pwd)/runtime/duck-ui-data:/data" \
  ghcr.io/caioricciuti/duck-ui:latest
```

## Comparison with JupyterLab

| Feature | JupyterLab | duck-ui |
|---|---|---|
| Writing analysis code | Yes | Limited |
| SQL editor | Basic (jupysql) | Full-featured |
| Charts | All Python libs | Built-in simple charts |
| Notebooks | Yes | No |
| Data preview | `df.head()` | Interactive table |
| Script automation | Yes | No |
| Quick exploration | Medium | Fast |

**Use both:**

- duck-ui for quick data exploration and ad-hoc SQL
- JupyterLab for pipelines, ML, and reports

## Troubleshooting

### Docker daemon not running

- **Windows / macOS:** Start Docker Desktop from the Start menu
- **Linux:** `sudo systemctl start docker`

### Port 5522 already in use

```python
start_duck_ui(port=5523)
```

### Container starts but page doesn't load

```bash
docker ps
docker logs duck-ui
docker stop duck-ui
docker run -d --rm --name duck-ui -p 5522:5522 \
  ghcr.io/caioricciuti/duck-ui:latest
```

### "Cannot connect to Docker daemon"

```bash
groups | grep docker
sudo usermod -aG docker $USER
```

### Pull fails (offline)

On a machine with internet:

```bash
docker pull ghcr.io/caioricciuti/duck-ui:latest
docker save ghcr.io/caioricciuti/duck-ui:latest -o duck-ui.tar
```

Copy `duck-ui.tar` to the offline machine and load it:

```bash
docker load -i duck-ui.tar
```

## Next Steps

- [Local AI with llama.cpp](AI_MODELS.md)
- [RAG with your documents](RAG.md)
- [Offline installation](OFFLINE_INSTALL.md)
