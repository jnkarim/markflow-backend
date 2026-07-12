from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User


class AuthenticationEdgeCaseTests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            email="edge-auth@example.com",
            password=self.password,
            first_name="Edge",
        )

    def login(self):
        return self.client.post(
            "/api/auth/token/",
            {"email": self.user.email, "password": self.password},
            format="json",
        )

    def test_invalid_password_is_rejected(self):
        response = self.client.post(
            "/api/auth/token/",
            {"email": self.user.email, "password": "WrongPassword123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_refresh_token_issues_a_new_access_token(self):
        login_response = self.login()

        response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": login_response.data["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_logout_requires_a_refresh_token(self):
        login_response = self.login()
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )

        response = self.client.post("/api/auth/logout/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Refresh token is required.")

    def test_logout_blacklists_the_refresh_token(self):
        login_response = self.login()
        refresh = login_response.data["refresh"]
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )

        logout_response = self.client.post(
            "/api/auth/logout/",
            {"refresh": refresh},
            format="json",
        )
        self.client.credentials()
        refresh_response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": refresh},
            format="json",
        )

        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_log_out(self):
        response = self.client.post(
            "/api/auth/logout/",
            {"refresh": "not-a-real-token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
