import logging
import os
import socket
import subprocess
import threading

import click
from colorama import Fore, Style
from dotenv import load_dotenv
from flask import Flask, send_from_directory

import data_copilot

import enum


class BACKENDS(enum.Enum):
    SQL = "sql"
    LANGCHAIN = "langchain"


STANDARD_BACKEND = BACKENDS.SQL


def get_envs():
    env = {
        "JWT_SECRET_KEY": subprocess.check_output("openssl rand -hex 32", shell=True)
        .decode("utf-8")
        .strip(),
        "BACKEND_HOST": "localhost:8000/api",
        "DB_CONNECTION_STRING": "sqlite:///data_copilot.db",
        "CELERY_BROKER_URL": "redis://localhost:6378/0",
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        "STORAGE_BACKEND": "volume://shared-fs/data",
        "ENVIRONMENT": "DEVELOPMENT",
        "COMPUTE_BACKEND": os.environ.get("COMPUTE_BACKEND", STANDARD_BACKEND),
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "AZURE_STORAGE_ACCOUNT_KEY": "",
        "AZURE_STORAGE_ACCOUNT_NAME": "",
        "CONTAINER_NAME": "",
    }
    return env


def start_backend_server(log_level="INFO"):
    if log_level.lower() not in (
        "critical",
        "error",
        "warning",
        "info",
        "debug",
        "trace",
    ):
        log_level = "info"
    backend_process = subprocess.Popen(
        [
            "uvicorn",
            "data_copilot.backend.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--log-level",
            log_level.lower(),
        ],
        env=get_envs(),
        stdout=subprocess.PIPE,  # Capture stdout
        stderr=subprocess.STDOUT,  # Redirect stderr to stdout
        universal_newlines=True,  # Enable text mode for stdout
    )
    return backend_process


def start_redis(log_level="INFO"):
    if log_level.lower() not in ("debug", "verbose", "notice", "warning"):
        log_level = "warning"

    redis_process = subprocess.Popen(
        [
            "redis-server",
            "--port",
            "6378",
            "--appendonly",
            "yes",
            "--loglevel",
            log_level.lower(),
        ],
        stdout=subprocess.PIPE,  # Capture stdout
        stderr=subprocess.STDOUT,  # Redirect stderr to stdout
        universal_newlines=True,  # Enable text mode for stdout)
    )
    return redis_process


def start_frontend(log_level="INFO"):
    def _start_frontend():
        # Set up a logger for this thread, with the specified log level
        logger = logging.getLogger("Frontend")
        logger.setLevel(log_level)

        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        logger.addHandler(handler)

        log = logging.getLogger("werkzeug")
        log.setLevel(log_level)

        path = os.path.join(data_copilot.__path__[0], "frontend", "dist")

        app = Flask("Frontend", static_folder=path)

        # Apply the logger to the app
        app.logger.handlers = [handler]

        @app.route("/assets/<path:path>")
        def send_assets(path):
            return send_from_directory(os.path.join(app.static_folder, "assets"), path)

        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def catch_all(path):
            return send_from_directory(app.static_folder, "index.html")

        app.run(host="0.0.0.0", port=8080)

    frontend_process = threading.Thread(target=_start_frontend, daemon=True)
    frontend_process.start()
    return frontend_process


def check_free_ports(ports=[8000, 8080, 6378]):
    non_free_ports = []
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                # try to open and bind to the socket
                sock.bind(("localhost", port))
            except OSError:
                non_free_ports.append(port)

    if len(non_free_ports) > 0:
        logging.warn(
            f"{Fore.YELLOW}"
            f"Ports {non_free_ports} are not free. "
            "Please make sure that the ports are free. "
            "Run 'lsof -i :<port>' to see which process "
            "is using the port."
        )


def start_worker(log_level="INFO"):
    worker_process = subprocess.Popen(
        [
            "celery",
            "-A",
            "data_copilot.celery_app.worker.execution_app",
            "worker",
            "--loglevel",
            log_level,
        ],
        env=get_envs(),
        stdout=subprocess.PIPE,  # Capture stdout
        stderr=subprocess.STDOUT,  # Redirect stderr to stdout
        universal_newlines=True,  # Enable text mode for stdout
    )
    return worker_process


def capture_stdout(color, process_name, process):
    while True:
        line = process.stdout.readline()
        if not line:
            continue
        print(f"{color}{process_name+':': <20} {Style.RESET_ALL}{line}", end="")


def create_subprocess_logger(**processes):
    COLORS = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

    threads = []
    for i, process in enumerate(processes):
        stdout_thread = threading.Thread(
            target=capture_stdout,
            kwargs=dict(
                color=COLORS[i], process_name=process, process=processes[process]
            ),
            daemon=True,
        )
        stdout_thread.start()
        threads.append(stdout_thread)


def kill_process(process):
    if process is not None:
        process.terminate()
        process.wait()
        process = None


@click.group()
def main():
    pass


@main.command(
    help=(
        "Start the Data Copilot. This will "
        "start the backend, redis, worker and "
        "frontend."
    )
)
@click.option(
    "--log-level",
    default="WARNING",
    help=("The log level to use. Defaults to WARNING."),
)
@click.option(
    "--backend",
    default=STANDARD_BACKEND.value,
    type=click.Choice([b.value for b in BACKENDS]),
    help=f"The backend to use for computation. Defaults to {STANDARD_BACKEND.value}",
)
def run(log_level, backend):
    # check_free_ports()

    load_dotenv(".env")

    os.environ["COMPUTE_BACKEND"] = backend
    if os.environ.get("OPENAI_API_KEY") is None:
        key = click.prompt("OpenAI API Key?", type=str, default="")

        # append to .env file and create if not exist
        with open(".env", "a") as f:
            f.write(f"OPENAI_API_KEY={key}\n")

    load_dotenv(".env")

    worker_process = start_worker(log_level)
    redis_process = start_redis(log_level)
    backend_process = start_backend_server(log_level)
    start_frontend(log_level)

    create_subprocess_logger(
        worker=worker_process,
        redis=redis_process,
        backend=backend_process,
    )

    try:
        # Keep the main thread alive
        while True:
            pass
    except KeyboardInterrupt:
        print("KeyboardInterrupt")

        kill_process(backend_process)
        kill_process(redis_process)
        kill_process(worker_process)

    exit(0)


@main.command()
@click.option("--yes", is_flag=True)
def reset(yes):
    if not yes:
        click.confirm("Are you sure you want to reset the database?", abort=True)

    # delete"appendonlydir, shared-fs, .env, data_copilot.db, dump.rdb
    subprocess.run(
        [
            "rm",
            "-rf",
            "appendonlydir",
            "shared-fs",
            ".env",
            "data_copilot.db",
            "dump.rdb",
        ]
    )


if __name__ == "__main__":
    main()
