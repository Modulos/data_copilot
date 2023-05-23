from data_copilot.backend.tests.utils import BasicTest


class TestUser(BasicTest):
    def test_users_me(self):
        response = self.client.get("/api/users/me", headers=self.auth_header)
        assert response.status_code == 200

    def test_users_me_unauthorized(self):
        response = self.client.get("/api/users/me")
        assert response.status_code == 401

    def test_users_me_groups(self):
        response = self.client.get("/api/users/me/groups", headers=self.auth_header)
        assert response.status_code == 200
        assert len(response.json().get("groups")) == 0

    def test_users_me_groups_unauthorized(self):
        response = self.client.get("/api/users/me/groups")
        assert response.status_code == 401
