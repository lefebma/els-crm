# Gunicorn configuration file
import multiprocessing
import os

# Server socket
port = os.environ.get('PORT', '8000')
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 600
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "crm_app"

# Application preloading
preload_app = True

# Server mechanics
daemon = False
pidfile = None
tmp_upload_dir = None

def when_ready(server):
    """Called just after the server is started."""
    # Create instance directory for SQLite
    import os
    os.makedirs("instance", exist_ok=True)
    print("Gunicorn server is ready. Instance directory created.")

def worker_init(worker):
    """Called just after a worker has been forked."""
    print(f"Worker {worker.pid} initialized")
