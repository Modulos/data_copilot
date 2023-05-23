import os
from datetime import datetime, timedelta
from functools import wraps
from io import BufferedIOBase
from typing import List, Optional, Tuple

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    FileSasPermissions,
    generate_file_sas,
)

from data_copilot.storage_handler.base import ClientABC

download_permissions = FileSasPermissions(read=True, list=True)
upload_permissions = FileSasPermissions(
    read=True, write=True, delete=True, add=True, create=True, list=True, tag=True
)

ACCOUNT_URL = "https://{account_name}.dfs.core.windows.net"


def _uri_to_account_name_and_container(uri: str) -> Tuple[Optional[str], ...]:
    """
    Parses a URI to an Azure account name and container name
    """
    if not uri:
        return None, None

    if "://" not in uri:
        raise ValueError("Could not parse account_url from uri")

    splitted = uri.split("://")[1].split("/")

    if len(splitted) < 2:
        raise ValueError("Could not parse account_url from uri")

    account_name = splitted[0].split(".")[0]
    container = splitted[1]
    folder = "/".join(splitted[2:])

    return account_name, container, folder


def path_processor(func):
    """
    Decorator to process paths
    """

    @wraps(func)
    def wrapper(self, path, *args, **kwargs):
        if not path:
            raise ValueError("Path cannot be empty")

        path.replace("abfss://", "https://")
        path.replace("abfs://", "https://")
        if self.fs_url in path:
            path = path.replace(self.fs_url, "")

        return func(self, path, *args, **kwargs)

    return wrapper


class AzureClient(ClientABC):
    def set_client(
        self,
        uri,
        credential=None,
        *args,
        **kwargs,
    ):
        if credential is None:
            credential = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")

        account_name, container, path = _uri_to_account_name_and_container(uri)

        self.uri = uri
        self.account_name = account_name
        self.container = container
        self.path = path
        self.account_url = ACCOUNT_URL.format(account_name=account_name)
        self.credential = credential
        self.fs_url = f"{self.account_url}/{self.container}"

        client = DataLakeServiceClient(
            account_url=self.account_url, credential=self.credential
        )
        fs = client.get_file_system_client(file_system=container)
        self.fs = fs

    @path_processor
    def read(self, path: str) -> BufferedIOBase:
        """
        Reads a file from a path
        """

        if not self.exists(path):
            raise FileNotFoundError(f"File {path} does not exist")

        return self.fs.get_file_client(path).download_file()

    @path_processor
    def write(self, path: str, data: str | BufferedIOBase) -> None:
        """
        Writes a bytes object or stream to a path
        """
        self.fs.get_file_client(path).upload_data(data, overwrite=True)

    @path_processor
    def list(self, path: str, recursive: bool = False) -> List[str]:
        """
        Show all files in that path
        """
        try:
            return [
                f.get("name") for f in self.fs.get_paths(path=path, recursive=recursive)
            ]

        except ResourceNotFoundError:
            return []

    @path_processor
    def delete(self, path: str) -> None:
        """
        Deletes a file from a path
        """
        if not self.exists(path):
            raise FileNotFoundError(f"File {path} does not exist")

        self.fs.get_file_client(path).delete_file()

    @path_processor
    def exists(self, path: str) -> bool:
        try:
            return self.fs.get_file_client(path).exists()
        except ResourceNotFoundError:
            return False

    @path_processor
    def get_signed_download_url(self, path: str, expires_in: int = 3600) -> str:
        """
        Returns a signed url for downloading a file
        """
        if not self.exists(path):
            raise FileNotFoundError(f"File {path} does not exist")

        dir_name, file_name = os.path.split(path)
        dir_name = dir_name.strip("/")
        file_name = file_name.strip("/")
        sas_token = generate_file_sas(
            account_name=self.account_name,
            file_system_name=self.container,
            directory_name=dir_name,
            file_name=file_name,
            credential=self.credential,
            permission=download_permissions,
            expiry=datetime.utcnow() + timedelta(seconds=expires_in),
        )
        path = path.strip("/")
        file_url = str(os.path.join(self.account_url, self.container, path))
        return f"{file_url}?{sas_token}"

    @path_processor
    def get_signed_upload_url(self, path: str, expires_in: int = 3600) -> str:
        """
        Returns a signed url for uploading a file
        """
        dir_name, file_name = os.path.split(path)
        dir_name = dir_name.strip("/")
        file_name = file_name.strip("/")
        sas_token = generate_file_sas(
            account_name=self.account_name,
            file_system_name=self.container,
            directory_name=dir_name,
            file_name=file_name,
            credential=self.credential,
            permission=upload_permissions,
            expiry=datetime.utcnow() + timedelta(seconds=expires_in),
        )
        path = path.strip("/")
        file_url = str(os.path.join(self.account_url, self.container, path))
        return f"{file_url}?{sas_token}"

    @path_processor
    def get_size(self, path: str) -> int:
        """
        Returns the size of a file
        """
        if not self.exists(path):
            raise FileNotFoundError(f"File {path} does not exist")

        return self.fs.get_file_client(path).get_file_properties().size
