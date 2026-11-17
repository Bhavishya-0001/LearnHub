from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User


class AccountsAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_student_registration(self):
        url = reverse("auth-register")
        data = {
            "name": "Alice Student",
            "email": "alice@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", res.data)
        self.assertIn("access", res.data["tokens"])
        self.assertEqual(res.data["user"]["role"], "student")

        user = User.objects.get(email="alice@example.com")
        self.assertEqual(user.role, "student")
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password("Password123!"))

    def test_duplicate_email_registration_fails(self):
        url = reverse("auth-register")
        data = {
            "name": "First User",
            "email": "duplicate@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        }
        res1 = self.client.post(url, data)
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        res2 = self.client.post(url, data)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success_and_jwt_tokens(self):
        User.objects.create_user(
            email="login_test@example.com",
            password="StrongPassword123!",
            name="Login Tester"
        )
        url = reverse("auth-login")
        res = self.client.post(url, {
            "email": "login_test@example.com",
            "password": "StrongPassword123!"
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.data["user"]["email"], "login_test@example.com")

    def test_login_failure_invalid_credentials(self):
        url = reverse("auth-login")
        res = self.client.post(url, {
            "email": "nonexistent@example.com",
            "password": "WrongPassword"
        })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
