from functools import wraps

from data_copilot.storage_handler.base import ClientABC


def _get_client(func):
    @wraps(func)
    def wrapper(uri, *args, **kwargs):
        if "dfs.core.windows.net" in uri:
            from data_copilot.storage_handler.azure_client import AzureClient

            client = AzureClient(uri)
        elif uri.startswith("volume://") or uri.startswith("file://"):
            from data_copilot.storage_handler.localstorage_client import (
                LocalStorageClient,
            )

            client = LocalStorageClient(uri)
        else:
            raise ValueError(f"Could not parse account_url {uri}")

        return func(client, uri, *args, **kwargs)

    return wrapper


@_get_client
def list_files(client: ClientABC, uri, *args, **kwargs):
    return client.list(uri, *args, **kwargs)


@_get_client
def read_file(client: ClientABC, uri, *args, **kwargs):
    return client.read(uri, *args, **kwargs)


@_get_client
def write_file(client: ClientABC, uri, data, *args, **kwargs):
    return client.write(uri, data=data, *args, **kwargs)


@_get_client
def delete_file(client: ClientABC, uri, *args, **kwargs):
    return client.delete(uri, *args, **kwargs)


@_get_client
def exists(client: ClientABC, uri, *args, **kwargs):
    return client.exists(uri, *args, **kwargs)


@_get_client
def get_size(client: ClientABC, uri, *args, **kwargs):
    return client.get_size(uri, *args, **kwargs)


@_get_client
def get_signed_download_url(client: ClientABC, uri, *args, **kwargs):
    return client.get_signed_download_url(uri, *args, **kwargs)


@_get_client
def get_signed_upload_url(client: ClientABC, uri, *args, **kwargs):
    return client.get_signed_upload_url(uri, *args, **kwargs)
