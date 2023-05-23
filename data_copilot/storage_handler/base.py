from abc import ABC, abstractmethod
from io import BufferedIOBase, BufferedReader
from typing import Generator


class ClientABC(ABC):
    def __init__(self, *args, **kwargs):
        self.set_client(*args, **kwargs)

    @abstractmethod
    def set_client(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def read(self, path: str) -> BufferedIOBase | BufferedReader:
        pass

    @abstractmethod
    def write(self, path: str, data: str | BufferedIOBase) -> None:
        """
        Writes a bytes object or stream to a path
        """
        pass

    @abstractmethod
    def list(
        self, path: str, recursive: bool = False
    ) -> list[str] | Generator[str, None, None]:
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def get_signed_download_url(self, path: str, expires_in: int = 3600) -> str:
        pass

    @abstractmethod
    def get_signed_upload_url(self, path: str, expires_in: int = 3600) -> str:
        pass

    @abstractmethod
    def get_size(self, path: str) -> str:
        pass
