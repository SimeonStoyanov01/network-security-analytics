# Network Security Analytics — Developer quick-start

Follow these steps to set up a local development environment, build the CICFlowMeter image and run the three main processes: watcher, Celery worker, and FastAPI server.

Prerequisites
- Docker (for building/running CICFlowMeter image)
- Python 3.10+ and virtualenv
- Redis (can be run as local service or Docker container)

1) Create a Python virtual environment and install dependencies

**For Windowns**
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
**For Linux**
````bash
# On WSL / Linux (copy-paste into your project root)
sudo apt update
# ensure venv support and pip are available on the system
sudo apt install -y python3-venv python3-pip
# create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate
# upgrade pip inside the venv and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
````

2) Build the CICFlowMeter Docker image (this is the canonical image that provides the `cfm` CLI)


```bash
# Build image called cicflowmeter:offline
cd CICFlowMeter
docker build -t cicflowmeter:offline
```

3) Start Redis (local service)

For developers using WSL, running Redis directly as a system service is a convenient alternative to Docker.

```bash
# In your WSL terminal (e.g., Ubuntu)
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

Alternatively, you can start Redis with Docker as originally suggested:


```bash
# Run Redis in Docker (recommended for dev):
docker run -d --name redis-local -p 6379:6379 redis:7-alpine
```

4) Run the project processes (in separate terminals)

- Start the watcher (watches `data/input` and enqueues jobs)

```bash
# Terminal A
source .venv/bin/activate
cd src
python watcher.py
```

- Start a Celery worker (processes queued PCAPs and runs the classifier)

```bash
# Terminal B
source .venv/bin/activate
cd src
# run a Celery worker that imports the module where tasks are defined
celery -A workers.flow worker --loglevel=info
```

- Start the FastAPI server (accepts uploads and enqueues jobs)

```bash
# Terminal C
source .venv/bin/activate
cd src
uvicorn app.server:app --reload --host 0.0.0.0 --port 8000
```

Notes
- Ensure `data/input` and `data/out` directories exist and are writable by these processes. The watcher and server will place PCAPs into `data/input` and the worker will write outputs under `data/out`.

"""
