# Linux Installation Guide

This guide covers installation of the DuckDB Toolkit on
Linux (Ubuntu, Debian, Fedora, Arch, and derivatives).

## Prerequisites

The toolkit installs Python and DuckDB inside the project folder, so
you do NOT need system Python to run the toolkit. However, a system
Python 3.9+ is needed to bootstrap `setup.py`.

### Install system packages

**Debian / Ubuntu:**

```bash
sudo apt update
sudo apt install -y curl wget tar gzip ca-certificates python3
```

**Fedora / RHEL:**

```bash
sudo dnf install -y curl wget tar gzip ca-certificates python3
```

**Arch:**

```bash
sudo pacman -S --needed curl wget tar gzip ca-certificates python
```

### Verify Python

```bash
python3 --version
# Must be 3.9 or newer
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/duckdb-portable-toolkit.git
cd duckdb-portable-toolkit
```

### 2. Run the setup script

```bash
python3 setup.py
```

Choose a profile:

| # | Profile | Size |
|---|---|---|
| 1 | light | ~500 MB |
| 2 | standard | ~3-4 GB |
| 3 | full | ~10-12 GB |
| 4 | custom | varies |

Or skip the prompt:

```bash
python3 setup.py --profile standard
```

### 3. Verify installation

```bash
python3 verify.py
```

All checks should show `[ok]`. If any fail, re-run `python3 setup.py`.

## Running the toolkit

### Launch JupyterLab

```bash
chmod +x start-jupyter.sh   # first time only
./start-jupyter.sh
```

Or from the terminal directly:

```bash
runtime/python/bin/python3 -m jupyterlab --ip=0.0.0.0 --port=8888
```

- `--ip=0.0.0.0` makes it accessible from other machines on the LAN
- Remove it to bind to localhost only

Then open `http://localhost:8888` in your browser.

### Launch a Streamlit dashboard

```bash
chmod +x start-streamlit.sh
./start-streamlit.sh
```

Or directly:

```bash
runtime/python/bin/python3 -m streamlit run \
    dashboards/01_orders_dashboard.py \
    --server.port 8501 \
    --server.address 0.0.0.0
```

### DuckDB CLI

```bash
runtime/duckdb/duckdb my_database.duckdb
```

### Run manifest generator

```bash
runtime/python/bin/python3 mcp/manifest_generator.py
```

## Networking

### Access from another machine on the LAN

1. Bind to `0.0.0.0` (see commands above)
2. Find your IP:

   ```bash
   ip addr show | grep "inet "
   # or
   hostname -I
   ```

3. Open the firewall (if `ufw` is active):

   ```bash
   sudo ufw allow 8888/tcp      # JupyterLab
   sudo ufw allow 8501/tcp      # Streamlit
   sudo ufw allow 5522/tcp      # duck-ui
   sudo ufw allow 8080/tcp      # llama.cpp server
   ```

4. Colleagues open `http://YOUR-IP:8888/lab` in their browser.

### SSH tunnel (safer alternative)

```bash
# On your local machine
ssh -L 8888:localhost:8888 user@server
```

Then open `http://localhost:8888/lab` locally.

## Running in the background

### Using `nohup`

```bash
nohup ./start-jupyter.sh > logs/jupyter.log 2>&1 &
```

### Using `systemd` (permanent service)

Create `/etc/systemd/system/duckdb-toolkit.service`:

```ini
[Unit]
Description=DuckDB Toolkit - JupyterLab
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/home/YOUR_USER/duckdb-portable-toolkit
ExecStart=/home/YOUR_USER/duckdb-portable-toolkit/runtime/python/bin/python3 -m jupyterlab --ip=0.0.0.0 --port=8888 --no-browser
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable duckdb-toolkit
sudo systemctl start duckdb-toolkit
sudo systemctl status duckdb-toolkit
```

## Common Issues

### Permission denied on scripts

```bash
chmod +x start-jupyter.sh start-streamlit.sh
chmod +x runtime/python/bin/*
chmod +x runtime/duckdb/duckdb
```

### Missing shared libraries

```bash
# Debian / Ubuntu
sudo apt install -y libpython3-dev

# Fedora
sudo dnf install -y python3-devel
```

### Port already in use

```bash
sudo lsof -i :8888
sudo netstat -tlnp | grep 8888
kill -9 <PID>
```

### Network download slow

```bash
curl -I https://github.com
curl -I https://pypi.org
python3 setup.py
```

Already-installed components are skipped (`skip_existing: true`).

## Uninstall

```bash
cd ..
rm -rf duckdb-portable-toolkit
```

## Next Steps

- [Connecting to duck-ui](CONNECT_DUCK_UI.md)
- [Local AI with llama.cpp](AI_MODELS.md)
- [RAG with your documents](RAG.md)
- [Offline installation](OFFLINE_INSTALL.md)
