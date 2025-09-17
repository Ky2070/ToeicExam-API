import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from asgiref.sync import sync_to_async
from Authentication.models import User
from Authentication.sse_manager import SSEManager
from Authentication.sse_views import notify_logout


class SSEManagerTest(TestCase):
    async def asyncSetUp(self):
        self.sse_manager = SSEManager()
        self.user_id = 1
        self.queue = asyncio.Queue()

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.asyncSetUp())

    def tearDown(self):
        self.loop.close()

    async def test_register_connection(self):
        """Test registering a new SSE connection"""
        self.sse_manager.register_connection(self.user_id, self.queue)
        self.assertIn(self.user_id, self.sse_manager.connections)
        self.assertIn(self.queue, self.sse_manager.connections[self.user_id])

    async def test_remove_connection(self):
        """Test removing an SSE connection"""
        self.sse_manager.register_connection(self.user_id, self.queue)
        self.sse_manager.remove_connection(self.user_id, self.queue)
        # Check if the queue was removed from the set
        if self.user_id in self.sse_manager.connections:
            self.assertNotIn(self.queue, self.sse_manager.connections[self.user_id])

    async def test_send_event(self):
        """Test sending an event to a connection"""
        self.sse_manager.register_connection(self.user_id, self.queue)
        event_type = "TEST_EVENT"
        event_data = {"message": "test message"}

        await self.sse_manager.send_event(self.user_id, event_type, event_data)

        try:
            # Get the message from the queue with timeout
            message = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            message_data = json.loads(message)

            self.assertEqual(message_data["type"], event_type)
            self.assertEqual(message_data["data"], event_data)
        except asyncio.TimeoutError:
            self.fail("Timeout waiting for event message")

    async def test_notify_logout(self):
        """Test sending force logout notification"""
        self.sse_manager.register_connection(self.user_id, self.queue)
        await notify_logout(self.user_id)

        try:
            # Get the message from the queue with timeout
            message = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            message_data = json.loads(message)

            self.assertEqual(message_data["type"], "FORCE_LOGOUT")
            self.assertIn("message", message_data["data"])
        except asyncio.TimeoutError:
            self.fail("Timeout waiting for logout message")


class SSEViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test user with unique email
        self.user_data = {
            "email": f"test{id(self)}@example.com",
            "username": f"testuser{id(self)}",
            "password": "testpass123",
        }

        self.user = User.objects.create_user(**self.user_data)

        # Get authentication tokens
        response = self.client.post(
            reverse("token_obtain"),
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
        )

        if response.status_code == status.HTTP_200_OK:
            self.access_token = response.data.get("access")
        else:
            self.access_token = None

    def test_sse_endpoint_authentication(self):
        """Test SSE endpoint requires authentication"""
        # Test without authentication
        response = self.client.get(reverse("sse_notifications"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        if self.access_token:
            # Test with authentication
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            response = self.client.get(reverse("sse_notifications"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.get("Content-Type"), "text/event-stream")

    def test_sse_connection_headers(self):
        """Test SSE connection has correct headers"""
        if self.access_token:
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            response = self.client.get(reverse("sse_notifications"))

            self.assertEqual(response.get("Cache-Control"), "no-cache")
            self.assertEqual(response.get("Connection"), "keep-alive")
            self.assertEqual(response.get("X-Accel-Buffering"), "no")

    @patch("Authentication.sse_views.event_stream")
    def test_sse_stream_content(self, mock_event_stream):
        """Test SSE stream content format"""

        # Mock the event stream to return simple data
        def mock_stream(request):
            yield 'data: {"type":"heartbeat","data":null}\n\n'
            yield 'data: {"type":"FORCE_LOGOUT","data":{"message":"test"}}\n\n'

        mock_event_stream.return_value = mock_stream(None)

        if self.access_token:
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            response = self.client.get(reverse("sse_notifications"))

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.get("Content-Type"), "text/event-stream")


class IntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Create test user with unique email
        self.user_data = {
            "email": f"test{id(self)}@example.com",
            "username": f"testuser{id(self)}",
            "password": "testpass123",
        }

        self.user = User.objects.create_user(**self.user_data)

    def tearDown(self):
        self.loop.close()

    def test_login_triggers_force_logout(self):
        """Test that login from new device triggers force logout for old device"""

        async def run_test():
            # First device login
            login_data = {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            }

            response1 = self.client.post(reverse("token_obtain"), login_data)
            self.assertEqual(response1.status_code, status.HTTP_200_OK)
            token1 = response1.data.get("access")
            self.assertIsNotNone(token1, "Access token should be present")

            # Connect to SSE with first device
            sse_manager = SSEManager()
            queue1 = asyncio.Queue()
            sse_manager.register_connection(self.user.id, queue1)

            # Second device login
            response2 = self.client.post(reverse("token_obtain"), login_data)
            self.assertEqual(response2.status_code, status.HTTP_200_OK)

            try:
                # Check if first device received force logout
                message = await asyncio.wait_for(queue1.get(), timeout=1.0)
                message_data = json.loads(message)

                self.assertEqual(message_data["type"], "FORCE_LOGOUT")
                self.assertIn("message", message_data["data"])

                # Verify first device's token is invalid
                self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")
                response = self.client.get(reverse("user_profile"))
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            except asyncio.TimeoutError:
                self.fail("Timeout waiting for force logout message")

        self.loop.run_until_complete(run_test())
