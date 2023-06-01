from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch, MagicMock

import storage_handler.localstorage_client as lc


class LocalStorageClientTest(TestCase):
    def setUp(self) -> None:
        ovveride_custom_locations = {"volume": ""}
        mock_custom_location = MagicMock(spec=dict)
        mock_custom_location.__getitem__.side_effect = (
            ovveride_custom_locations.__getitem__
        )
        self.mock_custom_location = patch(
            "storage_handler.localstorage_client.custom_locations",
            new=mock_custom_location,
            spec=dict,
        )
        self.mock_custom_location.start()

        self.client = lc.LocalStorageClient()

        self.temp_dir = TemporaryDirectory()
        with open(Path(self.temp_dir.name) / "config.json", mode="wt"):
            self.confg_file = Path(self.temp_dir.name) / "config.json"
        with open(Path(self.temp_dir.name) / "data_file.bin", mode="wb"):
            self.content_file = Path(self.temp_dir.name) / "data_file.bin"

    def tearDown(self) -> None:
        self.mock_custom_location.stop()
        return super().tearDown()

    def test_list(self):
        res = self.client.list(f"volume://{self.temp_dir.name}")
        expected_res = [
            Path(self.temp_dir.name) / "config.json",
            Path(self.temp_dir.name) / "data_file.bin",
        ]

        self.assertListEqual(list(res), expected_res)

    def test_exists(self):
        self.assertTrue(self.client.exists(f"volume://{self.content_file}"))

    def test_write_read_delete(self):
        new_txt_file = f"volume://{self.temp_dir.name}/new_txt_content.csv"
        new_bin_file = f"volume://{self.temp_dir.name}/new_binary_content.bin"

        with BytesIO() as stream:
            stream.write(b"some new data")
            self.client.write(new_bin_file, stream)

        self.client.write(new_txt_file, "some new data")

        config = self.client.read(new_txt_file)
        self.assertEqual(config.read(), b"some new data")

        content = self.client.read(new_bin_file)
        self.assertEqual(content.read(), b"some new data")

        self.client.delete(new_txt_file)
        self.client.delete(new_bin_file)

        with self.assertRaises(FileNotFoundError):
            self.client.delete(new_bin_file)

        with self.assertRaises(OSError):
            self.client.delete(self.temp_dir.name)
