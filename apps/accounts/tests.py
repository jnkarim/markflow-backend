from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User


class AuthenticationApiTests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            email="person@example.com",
            password=self.password,
            first_name="Alex",
        )

    def test_email_is_the_login_identifier(self):
        self.assertEqual(self.user.get_username(), "person@example.com")

    def test_user_can_log_in_with_email_and_password(self):
        response = self.client.post(
            reverse("accounts:token-obtain-pair"),
            {"email": self.user.email, "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_me_endpoint_requires_authentication(self):
        response = self.client.get(reverse("accounts:me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_endpoint_returns_current_user(self):
        token_response = self.client.post(
            reverse("accounts:token-obtain-pair"),
            {"email": self.user.email, "password": self.password},
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )

        response = self.client.get(reverse("accounts:me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["first_name"], "Alex")
