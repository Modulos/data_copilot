from io import BytesIO, StringIO
from unittest.mock import patch

import pandas as pd
from xlwt import Workbook

from data_copilot.backend.artifacts.artifact import CreateArtifactVersionCM
from data_copilot.backend.schemas.artifacts import ArtifactTypes
from data_copilot.backend.tests.utils import BasicTest

_XLS_TYPE = "application/vnd.ms-excel"
_XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class TestArtifacts(BasicTest):
    def setUp(self):
        self.columns = [
            "dteday",
            "season",
            "yr",
            "mnth",
            "holiday",
            "weekday",
            "workingday",
            "weathersit",
            "temp",
            "atemp",
            "hum",
            "windspeed",
            "casual",
            "registered",
            "cnt",
        ]
        self.row = [
            "2011-01-01",
            1,
            0,
            1,
            0,
            6,
            0,
            2,
            0.344167,
            0.363625,
            0.805833,
            0.160446,
            331,
            654,
            985,
        ]
        self.delimiters = [",", ";", "\t"]

    @patch.object(CreateArtifactVersionCM, "write")
    def test_unsupported_content_upload(self, _):
        with BytesIO() as xlsx_buffer:
            response = self.client.post(
                f"/api/artifacts/types/{ArtifactTypes.dataset}",
                headers=self.auth_header,
                json={"name": "testfile.txt"},
            )
            assert response.status_code == 201

            data_frame = pd.DataFrame(columns=self.columns)

            data_frame.to_excel(xlsx_buffer, index=False)
            xlsx_buffer.seek(0)

            artifact_id = response.json().get("id")
            response = self.client.post(
                f"/api/artifacts/id/{artifact_id}/versions",
                headers=self.auth_header,
                files={"file": ("filename", xlsx_buffer, "text/unknown")},
            )

            assert response.status_code == 500

    @patch.object(CreateArtifactVersionCM, "write")
    def test_csv_artifact_upload(self, _):
        for delimiter in self.delimiters:
            with StringIO() as csv_content:
                csv_content.write(delimiter.join(self.columns))
                csv_content.write("\n")
                csv_content.write(delimiter.join(map(str, self.row)))
                csv_content.seek(0)

                response = self.client.post(
                    f"/api/artifacts/types/{ArtifactTypes.dataset}",
                    headers=self.auth_header,
                    json={"name": "testfile.csv"},
                )

                assert response.status_code == 201

                artifact_id = response.json().get("id")
                response = self.client.post(
                    f"/api/artifacts/id/{artifact_id}/versions",
                    headers=self.auth_header,
                    files={"file": ("filename", csv_content, "text/csv")},
                )

                assert response.status_code == 201

    @patch.object(CreateArtifactVersionCM, "write")
    def test_xls_artifact_upload(self, _):
        with BytesIO() as xls_buffer:
            workbook = Workbook()
            worksheet = workbook.add_sheet("content")
            content = zip(self.columns, self.row)
            for i, (column, value) in enumerate(content):
                worksheet.write(0, i, column)
                worksheet.write(1, i, value)

            workbook.save(xls_buffer)
            xls_buffer.seek(0)

            response = self.client.post(
                f"/api/artifacts/types/{ArtifactTypes.dataset}",
                headers=self.auth_header,
                json={"name": "testfile.xls"},
            )

            assert response.status_code == 201

            artifact_id = response.json().get("id")
            response = self.client.post(
                f"/api/artifacts/id/{artifact_id}/versions",
                headers=self.auth_header,
                files={"file": ("filename", xls_buffer, _XLS_TYPE)},
            )

            assert response.status_code == 201

    @patch.object(CreateArtifactVersionCM, "write")
    def test_xlsx_artifact_upload(self, _):
        with BytesIO() as xlsx_buffer:
            data_frame = pd.DataFrame(columns=self.columns, data=[self.row])

            data_frame.to_excel(xlsx_buffer, index=False)
            xlsx_buffer.seek(0)

            response = self.client.post(
                f"/api/artifacts/types/{ArtifactTypes.dataset}",
                headers=self.auth_header,
                json={"name": "testfile.xlsx"},
            )

            assert response.status_code == 201

            artifact_id = response.json().get("id")
            response = self.client.post(
                f"/api/artifacts/id/{artifact_id}/versions",
                headers=self.auth_header,
                files={
                    "file": (
                        "filename",
                        xlsx_buffer,
                        _XLSX_TYPE,
                    )
                },
            )

            assert response.status_code == 201

    @patch.object(CreateArtifactVersionCM, "write")
    def test_csv_broken_artifact_upload(self, _):
        with StringIO() as csv_content:
            response = self.client.post(
                f"/api/artifacts/types/{ArtifactTypes.dataset}",
                headers=self.auth_header,
                json={"name": "testfile.csv"},
            )
            assert response.status_code == 201

            artifact_id = response.json().get("id")
            response = self.client.post(
                f"/api/artifacts/id/{artifact_id}/versions",
                headers=self.auth_header,
                files={"file": ("filename", csv_content, "text/csv")},
            )

            assert response.status_code == 500

        with StringIO() as csv_content:
            response = self.client.post(
                f"/api/artifacts/types/{ArtifactTypes.dataset}",
                headers=self.auth_header,
                json={"name": "testfile.csv"},
            )
            assert response.status_code == 201

            csv_content.write(";".join(self.columns))
            csv_content.write("\n")
            csv_content.seek(0)

            artifact_id = response.json().get("id")
            response = self.client.post(
                f"/api/artifacts/id/{artifact_id}/versions",
                headers=self.auth_header,
                files={"file": ("filename", csv_content, "text/csv")},
            )

            assert response.status_code == 500

        with StringIO() as csv_content:
            response = self.client.post(
                f"/api/artifacts/types/{ArtifactTypes.dataset}",
                headers=self.auth_header,
                json={"name": "testfile.csv"},
            )
            assert response.status_code == 201

            csv_content.write("dummystring")
            csv_content.seek(0)

            artifact_id = response.json().get("id")
            response = self.client.post(
                f"/api/artifacts/id/{artifact_id}/versions",
                headers=self.auth_header,
                files={"file": ("filename", csv_content, "text/csv")},
            )

            assert response.status_code == 500

    @patch.object(CreateArtifactVersionCM, "write")
    def test_xls_broken_artifact_upload(self, _):
        with BytesIO() as xls_buffer:
            response = self.client.post(
                f"/api/artifacts/types/{ArtifactTypes.dataset}",
                headers=self.auth_header,
                json={"name": "testfile.xls"},
            )
            assert response.status_code == 201

            artifact_id = response.json().get("id")
            response = self.client.post(
                f"/api/artifacts/id/{artifact_id}/versions",
                headers=self.auth_header,
                files={"file": ("filename", xls_buffer, _XLS_TYPE)},
            )

            assert response.status_code == 500

        with BytesIO() as xls_buffer:
            response = self.client.post(
                f"/api/artifacts/types/{ArtifactTypes.dataset}",
                headers=self.auth_header,
                json={"name": "testfile.xls"},
            )
            assert response.status_code == 201

            workbook = Workbook()
            worksheet = workbook.add_sheet("content")
            content = zip(self.columns, self.row)
            for i, (column, value) in enumerate(content):
                worksheet.write(0, i, column)

            workbook.save(xls_buffer)
            xls_buffer.seek(0)

            artifact_id = response.json().get("id")
            response = self.client.post(
                f"/api/artifacts/id/{artifact_id}/versions",
                headers=self.auth_header,
                files={"file": ("filename", xls_buffer, _XLS_TYPE)},
            )

            assert response.status_code == 500

        with BytesIO() as xls_buffer:
            response = self.client.post(
                f"/api/artifacts/types/{ArtifactTypes.dataset}",
                headers=self.auth_header,
                json={"name": "testfile.xls"},
            )
            assert response.status_code == 201

            workbook = Workbook()
            workbook.add_sheet("content")
            workbook.save(xls_buffer)
            xls_buffer.seek(0)

            artifact_id = response.json().get("id")
            response = self.client.post(
                f"/api/artifacts/id/{artifact_id}/versions",
                headers=self.auth_header,
                files={"file": ("filename", xls_buffer, _XLS_TYPE)},
            )

            assert response.status_code == 500

    @patch.object(CreateArtifactVersionCM, "write")
    def test_xlsx_broken_artifact_upload(self, _):
        with BytesIO() as xlsx_buffer:
            response = self.client.post(
                f"/api/artifacts/types/{ArtifactTypes.dataset}",
                headers=self.auth_header,
                json={"name": "testfile.xlsx"},
            )
            assert response.status_code == 201

            artifact_id = response.json().get("id")
            response = self.client.post(
                f"/api/artifacts/id/{artifact_id}/versions",
                headers=self.auth_header,
                files={
                    "file": (
                        "filename",
                        xlsx_buffer,
                        _XLSX_TYPE,
                    )
                },
            )

            assert response.status_code == 500

        with BytesIO() as xlsx_buffer:
            response = self.client.post(
                f"/api/artifacts/types/{ArtifactTypes.dataset}",
                headers=self.auth_header,
                json={"name": "testfile.xlsx"},
            )
            assert response.status_code == 201

            data_frame = pd.DataFrame(columns=self.columns)

            data_frame.to_excel(xlsx_buffer, index=False)
            xlsx_buffer.seek(0)

            artifact_id = response.json().get("id")
            response = self.client.post(
                f"/api/artifacts/id/{artifact_id}/versions",
                headers=self.auth_header,
                files={
                    "file": (
                        "filename",
                        xlsx_buffer,
                        _XLSX_TYPE,
                    )
                },
            )

            assert response.status_code == 500

        with BytesIO() as xlsx_buffer:
            response = self.client.post(
                f"/api/artifacts/types/{ArtifactTypes.dataset}",
                headers=self.auth_header,
                json={"name": "testfile.xlsx"},
            )
            assert response.status_code == 201

            data_frame = pd.DataFrame(columns=[])
            data_frame.to_excel(xlsx_buffer, index=False)
            xlsx_buffer.seek(0)

            artifact_id = response.json().get("id")
            response = self.client.post(
                f"/api/artifacts/id/{artifact_id}/versions",
                headers=self.auth_header,
                files={
                    "file": (
                        "filename",
                        xlsx_buffer,
                        _XLSX_TYPE,
                    )
                },
            )

            assert response.status_code == 500
