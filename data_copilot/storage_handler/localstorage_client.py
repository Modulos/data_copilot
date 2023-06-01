import os
from functools import wraps
from io import BufferedIOBase, BufferedReader
from pathlib import Path
from typing import Generator

from data_copilot.storage_handler.base import ClientABC


def path_processor(func):
    """
    Decorator to process paths
    """

    @wraps(func)
    def wrapper(self, path, *args, **kwargs):
        if not path:
            raise ValueError("Path cannot be empty")

        if path.startswith("volume://"):
            path = path.replace("volume://", "").replace("//", "/")

        elif path.startswith("file://"):
            path = path.replace("file://", "").replace("//", "/")

        return func(self, path, *args, **kwargs)

    return wrapper


class LocalStorageClient(ClientABC):
    def set_client(
        self,
        *args,
        **kwargs,
    ):
        ...

    @path_processor
    def read(self, path: str) -> BufferedReader:
        """
        Reads a file from a path
        """
        if not self.exists(path):
            raise FileNotFoundError(f"File {path} does not exist")

        return open(path, "rb")

    @path_processor
    def write(self, path: str, data: str | BufferedIOBase) -> None:
        """
        Writes a bytes object or stream to a path
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        if isinstance(data, str):
            with open(path, "wt") as file:
                file.write(data)
        elif hasattr(data, "write"):
            with open(path, "wb") as file:
                data.seek(0)
                file.write(data.read())
        else:
            raise Exception(f"Unsupported content/stream format {type(data)}")

    @path_processor
    def list(self, path: str, recursive: bool = False) -> Generator[str, None, None]:
        """
        Return file list generator in that path
        """
        return (item for item in Path(path).iterdir())

    @path_processor
    def delete(self, path: str) -> None:
        """
        Deletes a file from a path
        """
        if not self.exists(path):
            raise FileNotFoundError(f"File {path} does not exist")

        try:
            os.remove(path)
        except OSError:
            raise OSError(f"Removing directory {path}")

    @path_processor
    def exists(self, path: str) -> bool:
        return Path(path).exists()

    def get_signed_download_url(self, path: str, expires_in: int = 3600) -> str:
        """
        Returns a signed url for downloading a file
        """
        if not self.exists(path):
            raise FileNotFoundError(f"File {path} does not exist")

        return path

    @path_processor
    def get_signed_upload_url(self, path: str, expires_in: int = 3600) -> str:
        """
        Returns a signed url for uploading a file
        """
        return path

    @path_processor
    def get_size(self, path: str) -> int:
        """
        Returns the size of a file
        """
        if not self.exists(path):
            raise FileNotFoundError(f"File {path} does not exist")

        return Path(path).stat().st_size
