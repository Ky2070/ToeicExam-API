from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from Authentication.models import User
from .models import Message
import json


class ChatBotAPITestCase(APITestCase):
    """Test cases for Chat Bot API endpoints"""

    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            email="testuser1@example.com",
            username="testuser1",
            password="testpassword123",
        )
        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            username="testuser2",
            password="testpassword123",
        )

        # Create test messages
        self.message1 = Message.objects.create(
            user=self.user1, role="user", content="Hello, this is a test message"
        )
        self.message2 = Message.objects.create(
            user=self.user1, role="bot", content="Hi! How can I help you today?"
        )
        self.message3 = Message.objects.create(
            user=self.user2, role="user", content="This is user2 message"
        )

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied"""

        # Test GET messages
        url = reverse("chat_bot:user_messages")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test POST message
        response = self.client.post(url, {"role": "user", "content": "test"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test GET specific message
        url = reverse(
            "chat_bot:message_detail", kwargs={"message_id": self.message1.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_messages(self):
        """Test GET /messages/ - Get user's own messages"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("chat_bot:user_messages")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["count"], 2)  # user1 has 2 messages

        # Verify only user1's messages are returned
        message_ids = [msg["id"] for msg in response.data["data"]]
        self.assertIn(self.message1.id, message_ids)
        self.assertIn(self.message2.id, message_ids)
        self.assertNotIn(
            self.message3.id, message_ids
        )  # user2's message should not be included

    def test_create_message(self):
        """Test POST /messages/ - Create new message (conversation)"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("chat_bot:user_messages")
        new_message_data = {"content": "This is a new test message"}

        response = self.client.post(url, new_message_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

        # Check that both user and bot messages were created
        self.assertIn("user_message", response.data["data"])
        self.assertIn("bot_message", response.data["data"])

        # Verify user message
        user_message = response.data["data"]["user_message"]
        self.assertEqual(user_message["content"], "This is a new test message")
        self.assertEqual(user_message["role"], "user")
        self.assertEqual(user_message["user"], self.user1.id)

        # Verify bot message
        bot_message = response.data["data"]["bot_message"]
        self.assertEqual(bot_message["role"], "bot")
        self.assertEqual(bot_message["user"], self.user1.id)
        self.assertTrue(
            len(bot_message["content"]) > 0
        )  # Bot should respond with something

    def test_get_message_detail_owner(self):
        """Test GET /messages/{id}/ - Get message detail as owner"""
        self.client.force_authenticate(user=self.user1)

        url = reverse(
            "chat_bot:message_detail", kwargs={"message_id": self.message1.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(
            response.data["data"]["content"], "Hello, this is a test message"
        )

    def test_get_message_detail_not_owner(self):
        """Test GET /messages/{id}/ - Access denied for non-owner"""
        self.client.force_authenticate(user=self.user1)

        # Try to access user2's message
        url = reverse(
            "chat_bot:message_detail", kwargs={"message_id": self.message3.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_update_message_owner(self):
        """Test PUT /messages/{id}/ - Update message as owner"""
        self.client.force_authenticate(user=self.user1)

        url = reverse(
            "chat_bot:message_detail", kwargs={"message_id": self.message1.id}
        )
        update_data = {"content": "Updated message content"}

        response = self.client.put(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["content"], "Updated message content")

    def test_update_message_not_owner(self):
        """Test PUT /messages/{id}/ - Access denied for non-owner"""
        self.client.force_authenticate(user=self.user1)

        # Try to update user2's message
        url = reverse(
            "chat_bot:message_detail", kwargs={"message_id": self.message3.id}
        )
        update_data = {"content": "Trying to update"}

        response = self.client.put(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_delete_message_owner(self):
        """Test DELETE /messages/{id}/ - Delete message as owner"""
        self.client.force_authenticate(user=self.user1)

        url = reverse(
            "chat_bot:message_detail", kwargs={"message_id": self.message1.id}
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        # Verify message was deleted
        self.assertFalse(Message.objects.filter(id=self.message1.id).exists())

    def test_delete_message_not_owner(self):
        """Test DELETE /messages/{id}/ - Access denied for non-owner"""
        self.client.force_authenticate(user=self.user1)

        # Try to delete user2's message
        url = reverse(
            "chat_bot:message_detail", kwargs={"message_id": self.message3.id}
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

        # Verify message was not deleted
        self.assertTrue(Message.objects.filter(id=self.message3.id).exists())

    def test_conversation_history(self):
        """Test GET /messages/history/ - Get conversation history"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("chat_bot:conversation_history")

        # Test without limit
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["count"], 2)

        # Test with limit
        response = self.client.get(url + "?limit=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["count"], 1)

    def test_clear_conversation(self):
        """Test DELETE /messages/clear/ - Clear all user messages"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("chat_bot:clear_conversation")
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        # Verify user1's messages were deleted but user2's remain
        self.assertEqual(Message.objects.filter(user=self.user1).count(), 0)
        self.assertEqual(Message.objects.filter(user=self.user2).count(), 1)

    def test_messages_by_role(self):
        """Test GET /messages/by-role/ - Get messages by role"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("chat_bot:messages_by_role")

        # Test valid role
        response = self.client.get(url + "?role=user")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["count"], 1)  # Only one 'user' message for user1

        # Test missing role parameter
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

        # Test invalid role
        response = self.client.get(url + "?role=invalid")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_message_count(self):
        """Test GET /messages/count/ - Get message count"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("chat_bot:message_count")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["count"], 2)

    def test_invalid_message_data(self):
        """Test validation errors for invalid message data"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("chat_bot:user_messages")

        # Test empty content
        invalid_data = {"content": ""}
        response = self.client.post(url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

        # Test missing content
        invalid_data = {}
        response = self.client.post(url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_conversation_creation(self):
        """Test conversation creation (user message triggers bot response)"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("chat_bot:user_messages")

        # Test conversation creation with different message types
        test_messages = [
            "Hello, how are you?",
            "Can you help me?",
            "Thank you for your help!",
            "What is the weather like today?",
            "Goodbye!",
        ]

        for content in test_messages:
            data = {"content": content}
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response.data["success"])

            # Verify both messages were created
            self.assertIn("user_message", response.data["data"])
            self.assertIn("bot_message", response.data["data"])

            user_message = response.data["data"]["user_message"]
            bot_message = response.data["data"]["bot_message"]

            # Verify user message
            self.assertEqual(user_message["content"], content)
            self.assertEqual(user_message["role"], "user")

            # Verify bot message
            self.assertEqual(bot_message["role"], "bot")
            self.assertTrue(len(bot_message["content"]) > 0)


class ChatBotModelsTestCase(TestCase):
    """Test cases for Chat Bot models"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpassword123",
        )

    def test_message_model(self):
        """Test Message model"""
        message = Message.objects.create(
            user=self.user, role="user", content="Test message content"
        )

        self.assertEqual(str(message), "user: Test message content...")
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Test message content")
        self.assertTrue(message.created_at)

    def test_message_choices(self):
        """Test Message role choices"""
        # Test all valid choices
        valid_roles = ["user", "bot", "system"]
        for role in valid_roles:
            message = Message.objects.create(
                user=self.user, role=role, content=f"Test {role} message"
            )
            self.assertEqual(message.role, role)

    def test_user_messages_relationship(self):
        """Test User-Message relationship"""
        # Create messages for user
        Message.objects.create(user=self.user, role="user", content="Message 1")
        Message.objects.create(user=self.user, role="bot", content="Message 2")
        Message.objects.create(user=self.user, role="system", content="Message 3")

        # Test relationship
        messages = self.user.messages.all()
        self.assertEqual(messages.count(), 3)

        # Test cascade delete
        self.user.delete()
        self.assertEqual(Message.objects.count(), 0)
