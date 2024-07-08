from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import CustomUser


class RegisterAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("register")

    def test_register_user_successfully(self):
        data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().email, "test@example.com")

    def test_register_user_with_existing_email(self):
        CustomUser.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )
        data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CustomUser.objects.count(), 1)


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("login")

        # Create a user for testing
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )

    def test_login_with_valid_credentials(self):
        # Send a POST request with valid credentials
        response = self.client.post(
            self.login_url,
            {"email": "test@example.com", "password": "password123"},
            format="json",
        )

        # Check that the response has a 200 OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the response data
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Login successful")
        self.assertIn("accessToken", response.data["data"])
        self.assertIn("user", response.data["data"])
        self.assertEqual(response.data["data"]["user"]["userId"], str(self.user.userId))
        self.assertEqual(
            response.data["data"]["user"]["firstName"], self.user.first_name
        )
        self.assertEqual(response.data["data"]["user"]["lastName"], self.user.last_name)
        self.assertEqual(response.data["data"]["user"]["email"], self.user.email)
        self.assertIsNone(response.data["data"]["user"]["phone"])

    def test_login_with_invalid_credentials(self):
        # Send a POST request with invalid credentials
        response = self.client.post(
            self.login_url,
            {"email": "test@example.com", "password": "wrongpassword"},
            format="json",
        )

        # Check that the response has a 401 Unauthorized status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Check the response data
        self.assertEqual(response.data["status"], "Bad Request")
        self.assertEqual(response.data["message"], "Authentication failed")
        self.assertEqual(response.data["statusCode"], 401)

    def test_login_with_missing_credentials(self):
        # Send a POST request with missing credentials
        response = self.client.post(
            self.login_url,
            {"email": "test@example.com"},
            format="json",
        )

        # Check that the response has a 401 Unauthorized Request status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Check the response data
        self.assertEqual(response.data["status"], "Bad Request")
        self.assertEqual(response.data["message"], "Authentication failed")
        self.assertEqual(response.data["statusCode"], 401)
