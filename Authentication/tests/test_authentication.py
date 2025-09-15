from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from Authentication.models import User
import json


class MultiDeviceAuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("token_obtain")
        self.refresh_url = reverse("token_refresh")
        self.user_profile_url = reverse("user_profile")

        # Create a test user
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
        }
        self.user = User.objects.create_user(**self.user_data)

    def login_on_device(self, device_name="Device A"):
        """Helper method to simulate login on a device"""
        response = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            f"Login failed on {device_name}",
        )
        return {
            "access": response.data["access"],
            "refresh": response.data["refresh"],
        }

    def verify_token_works(self, access_token, should_work=True):
        """Helper method to verify if an access token works"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.user_profile_url)
        expected_status = (
            status.HTTP_200_OK if should_work else status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            response.status_code,
            expected_status,
            f"Token validation incorrect. Expected {expected_status}, got {response.status_code}",
        )

    def refresh_token(self, refresh_token, should_work=True):
        """Helper method to attempt token refresh"""
        response = self.client.post(self.refresh_url, {"refresh": refresh_token})
        expected_status = (
            status.HTTP_200_OK if should_work else status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            response.status_code,
            expected_status,
            f"Token refresh incorrect. Expected {expected_status}, got {response.status_code}",
        )
        return response.data if should_work else None

    def test_single_device_login(self):
        """Test that initial login on a single device works correctly"""
        # Login on Device A
        tokens = self.login_on_device("Device A")

        # Verify access token works
        self.verify_token_works(tokens["access"], should_work=True)

        # Verify refresh token works
        refresh_result = self.refresh_token(tokens["refresh"], should_work=True)
        self.assertIn(
            "access", refresh_result, "Refresh should return new access token"
        )

    def test_second_device_login_invalidates_first(self):
        """Test that logging in on a second device invalidates the first device's access token"""
        # Login on Device A
        device_a_tokens = self.login_on_device("Device A")

        # Verify Device A tokens work
        self.verify_token_works(device_a_tokens["access"], should_work=True)

        # Login on Device B
        device_b_tokens = self.login_on_device("Device B")

        # Verify Device A access token no longer works
        self.verify_token_works(device_a_tokens["access"], should_work=False)

        # Verify Device B access token works
        self.verify_token_works(device_b_tokens["access"], should_work=True)

    def test_latest_device_refresh_token_works(self):
        """Test that refresh token from the latest device works"""
        # Login on Device A
        device_a_tokens = self.login_on_device("Device A")

        # Login on Device B
        device_b_tokens = self.login_on_device("Device B")

        # Verify Device B refresh token works
        refresh_result = self.refresh_token(
            device_b_tokens["refresh"], should_work=True
        )
        self.assertIn(
            "access", refresh_result, "Refresh should return new access token"
        )

        # Verify new access token from refresh works
        self.verify_token_works(refresh_result["access"], should_work=True)

    def test_multiple_sequential_logins(self):
        """Test that multiple sequential logins maintain only the latest device's tokens"""
        # Login on Device A
        device_a_tokens = self.login_on_device("Device A")

        # Login on Device B
        device_b_tokens = self.login_on_device("Device B")

        # Login on Device C
        device_c_tokens = self.login_on_device("Device C")

        # Verify only Device C tokens work
        self.verify_token_works(device_a_tokens["access"], should_work=False)
        self.verify_token_works(device_b_tokens["access"], should_work=False)
        self.verify_token_works(device_c_tokens["access"], should_work=True)

        # Verify Device C refresh works
        refresh_result = self.refresh_token(
            device_c_tokens["refresh"], should_work=True
        )
        self.verify_token_works(refresh_result["access"], should_work=True)

    def test_old_refresh_token_behavior(self):
        """Test behavior of refresh tokens from old devices"""
        # Login on Device A
        device_a_tokens = self.login_on_device("Device A")

        # Login on Device B
        device_b_tokens = self.login_on_device("Device B")

        # Try refreshing with Device A's refresh token (implementation dependent)
        refresh_result = self.refresh_token(
            device_a_tokens["refresh"], should_work=True
        )
        if refresh_result:
            # If old refresh tokens are allowed, verify the new access token works
            self.verify_token_works(refresh_result["access"], should_work=True)

            # Device B's access token should no longer work since a new token was issued
            self.verify_token_works(device_b_tokens["access"], should_work=False)

    def test_concurrent_refresh_requests(self):
        """Test handling of concurrent refresh requests from multiple devices"""
        # Login on multiple devices
        device_a_tokens = self.login_on_device("Device A")
        device_b_tokens = self.login_on_device("Device B")

        # Refresh tokens from both devices
        refresh_a = self.refresh_token(device_a_tokens["refresh"], should_work=True)
        refresh_b = self.refresh_token(device_b_tokens["refresh"], should_work=True)

        if refresh_a and refresh_b:
            # Only the latest refresh token's access token should work
            self.verify_token_works(refresh_a["access"], should_work=False)
            self.verify_token_works(refresh_b["access"], should_work=True)

            # Original access tokens should not work
            self.verify_token_works(device_a_tokens["access"], should_work=False)
            self.verify_token_works(device_b_tokens["access"], should_work=False)
