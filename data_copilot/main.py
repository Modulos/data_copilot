import os
from dotenv import load_dotenv
import subprocess
import threading
import data_copilot
import pandas

load_dotenv(".dev.local.env")
env = {
    "JWT_SECRET_KEY": subprocess.check_output("openssl rand -hex 32", shell=True)
    .decode("utf-8")
    .strip(),
    "BACKEND_HOST": "localhost:8000/api",
    "DB_CONNECTION_STRING": "sqlite:///data_copilot.db",
    "REDIS_URL": "redis://localhost:6379/0",
    "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
    "STORAGE_BACKEND": "volume:///data",
    "ENVIRONMENT": "DEVELOPMENT",
    "COMPUTE_BACKEND": "sql",
    "PATH": os.environ.get("PATH", ""),
    "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
    "AZURE_STORAGE_ACCOUNT_KEY": "",
    "AZURE_STORAGE_ACCOUNT_NAME": "",
    "CONTAINER_NAME": "",
}


def start_backend_server():
    backend_process = subprocess.Popen(
        [
            "uvicorn",
            "data_copilot.backend.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--log-level",
            "debug",
        ],
        env=env,
        stdout=subprocess.PIPE,  # Capture stdout
        stderr=subprocess.STDOUT,  # Redirect stderr to stdout
        universal_newlines=True,  # Enable text mode for stdout
    )
    return backend_process


def start_redis():
    redis_process = subprocess.Popen(
        ["redis-server", "--port", "6379", "--appendonly", "yes"],
        stdout=subprocess.PIPE,  # Capture stdout
        stderr=subprocess.STDOUT,  # Redirect stderr to stdout
        universal_newlines=True,  # Enable text mode for stdout)
    )
    return redis_process


def start_frontend():
    # path: data_copilot.frontend.dist
    # serve with python -m http.server 8080

    # cd data_copilot/frontend/dist
    # python -m http.server 8080
    path = os.path.join(data_copilot.__path__[0], "frontend", "dist")
    frontend_process = subprocess.Popen(
        [
            "python",
            "-m",
            "http.server",
            "8080",
        ],
        cwd=path,  # Set the working directory for the subprocess
        stdout=subprocess.PIPE,  # Capture stdout
        stderr=subprocess.STDOUT,  # Redirect stderr to stdout
        universal_newlines=True,  # Enable text mode for stdout
    )
    return frontend_process


def start_worker():
    worker_process = subprocess.Popen(
        [
            "celery",
            "-A",
            "data_copilot.celery_app.worker.execution_app",
            "worker",
        ],
        env=env,
        stdout=subprocess.PIPE,  # Capture stdout
        stderr=subprocess.STDOUT,  # Redirect stderr to stdout
        universal_newlines=True,  # Enable text mode for stdout
    )
    return worker_process


def capture_stdout(*processes):
    while True:
        for process in processes:
            line = process.stdout.readline()
            if not line:
                break
            print(line.rstrip())  # Process the captured line as needed


def kill_process(process):
    if process is not None:
        process.terminate()
        process.wait()
        process = None


if __name__ == "__main__":
    worker_process = start_worker()
    redis_process = start_redis()
    backend_process = start_backend_server()
    frontend_process = start_frontend()

    stdout_thread = threading.Thread(
        target=capture_stdout,
        args=(
            worker_process,
            # backend_process,
            # redis_process,
            # frontend_process,
        ),
        daemon=True,
    )
    stdout_thread.start()

    try:
        # Keep the main thread alive
        while True:
            pass
    except KeyboardInterrupt:
        print("KeyboardInterrupt")

        kill_process(backend_process)
        kill_process(redis_process)
        kill_process(frontend_process)
        kill_process(worker_process)

    stdout_thread.join()
