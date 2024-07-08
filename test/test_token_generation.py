from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.tokens import get_tokens_for_user

CustomUser = get_user_model()


class TokenGenerationTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )

    def test_get_tokens_for_user_returns_tokens(self):
        tokens = get_tokens_for_user(self.user)
        self.assertIn("refresh", tokens)
        self.assertIn("access", tokens)

    def test_access_token_contains_correct_user_details(self):
        tokens = get_tokens_for_user(self.user)
        access_token = tokens["access"]

        # Decode the access token to inspect its payload
        decoded_token = AccessToken(access_token).payload

        # self.assertEqual(tokens["refresh"], str(RefreshToken.for_user(self.user)))
        self.assertEqual(decoded_token["userId"], str(self.user.userId))
        self.assertEqual(decoded_token["email"], self.user.email)

    def test_refresh_token_contains_correct_user_details(self):
        tokens = get_tokens_for_user(self.user)
        refresh_token = tokens["refresh"]

        # Decode the refresh token to inspect its payload
        decoded_token = RefreshToken(refresh_token).payload

        self.assertEqual(decoded_token["userId"], str(self.user.userId))
        self.assertEqual(decoded_token["email"], self.user.email)


class GetTokensForUserTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )

    def test_get_tokens_for_user_returns_tokens(self):
        tokens = get_tokens_for_user(self.user)
        self.assertIn("refresh", tokens)
        self.assertIn("access", tokens)

    def test_refresh_token_contains_correct_user_details(self):
        tokens = get_tokens_for_user(self.user)
        refresh_token = tokens["refresh"]

        # Decode the refresh token to inspect its payload
        decoded_token = RefreshToken(refresh_token).payload

        self.assertEqual(decoded_token["userId"], str(self.user.userId))
        self.assertEqual(decoded_token["email"], self.user.email)
