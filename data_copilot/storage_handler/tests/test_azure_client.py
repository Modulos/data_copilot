import os
from unittest import TestCase
from unittest import mock

from data_copilot.storage_handler.azure_client import AzureClient, ACCOUNT_URL


def _get_mock_data_lake_service_client():
    mock_file_client = mock.Mock()
    mock_file_client.exists.return_value = True
    mock_file_client.download_file.return_value = "download_file"
    mock_file_client.upload_data = mock.Mock()

    mock_fs = mock.Mock()
    mock_fs.get_file_client.return_value = mock_file_client
    mock_fs.get_paths.return_value = [
        {"name": "/mock/path/to/file_1"},
        {"name": "/mock/path/to/file_2"},
    ]

    mock_client = mock.Mock()
    mock_client.get_file_system_client.return_value = mock_fs

    return mock_client


class AzureClientTest(TestCase):
    def setUp(self) -> None:
        account_name = "fake-account"
        container = "fake-container"
        credential = "fake-credential"
        uri = ACCOUNT_URL.format(account_name=account_name) + "/" + container

        with mock.patch(
            "storage_handler.azure_client.DataLakeServiceClient",
            return_value=_get_mock_data_lake_service_client(),
        ):
            self.azure_client = AzureClient(
                uri=uri,
                credential=credential,
            )

    def test_init(self):
        self.assertIsNotNone(self.azure_client)
        self.assertIsNotNone(self.azure_client.fs)

    def test_list(self):
        res = self.azure_client.list("/")
        expected_res = ["/mock/path/to/file_1", "/mock/path/to/file_2"]

        self.assertListEqual(res, expected_res)

    def test_exists(self):
        self.assertTrue(self.azure_client.exists("test.txt"))

    def test_read(self):
        res = self.azure_client.read("/")
        expected_res = "download_file"

        self.assertEqual(res, expected_res)

    def test_signed_url(self):
        mock_token = "fake-token"
        mock_dir = "path/to"
        mock_file = "file.csv"
        mock_path = os.path.join(mock_dir, mock_file)

        with mock.patch(
            "storage_handler.azure_client.generate_file_sas", return_value=mock_token
        ) as mock_gen_file_sas:
            res = self.azure_client.get_signed_download_url(mock_path)

        expected_res = (
            f"{self.azure_client.account_url}/"
            f"{self.azure_client.container}/"
            f"{mock_path}?{mock_token}"
        )

        self.assertEqual(res, expected_res)
        mock_gen_file_sas.assert_called_once_with(
            account_name=self.azure_client.account_name,
            file_system_name=self.azure_client.container,
            directory_name=mock_dir,
            file_name=mock_file,
            credential=self.azure_client.credential,
            permission=mock.ANY,
            expiry=mock.ANY,
        )

    def test_write(self):
        mock_data = b"Hello World"
        self.azure_client.write(
            "000/000/00.txt",
            mock_data,
        )

        self.azure_client.fs.get_file_client().upload_data.assert_called_once_with(
            mock_data, overwrite=True
        )
