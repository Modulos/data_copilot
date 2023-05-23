from data_copilot.backend.tests.utils import BasicTest


class TestAdmin(BasicTest):
    def test_admin_users_unauthorized(self):
        response = self.client.get("/api/admin/users", headers=self.auth_header)
        assert response.status_code == 400

    def test_admin_users(self):
        response = self.client.get("/api/admin/users", headers=self.admin_auth_header)
        assert response.status_code == 200
        assert len(response.json()) > 0

    def test_admin_users_create_unauthorized(self):
        response = self.client.post("/api/admin/users", headers=self.auth_header)
        assert response.status_code == 400

    def test_admin_users_create_delete(self):
        email = "testuser@pythontest.com"

        # check if user already exists
        response = self.client.get(
            f"/api/admin/users/query/{email}", headers=self.admin_auth_header
        )
        if response.status_code == 200:
            user_id = response.json().get("id")
            response = self.client.delete(
                f"/api/admin/users/{user_id}", headers=self.admin_auth_header
            )
            assert response.status_code == 204

        payload = {"email": email, "password": "string", "is_active": True}

        response = self.client.post(
            "/api/admin/users", headers=self.admin_auth_header, json=payload
        )
        assert response.status_code == 200
        user_id = response.json().get("id")

        response = self.client.delete(
            f"/api/admin/users/{user_id}", headers=self.admin_auth_header
        )
        assert response.status_code == 204
