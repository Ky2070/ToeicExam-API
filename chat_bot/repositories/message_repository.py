from typing import List, Optional
from django.db.models import QuerySet
from ..models import Message
from Authentication.models import User
from .base_repository import BaseRepository


class MessageRepository(BaseRepository):
    """Repository for Message model database operations"""

    def __init__(self):
        super().__init__(Message)

    def get_by_user_id(self, user_id: int) -> List[Message]:
        """Get all messages for a specific user by user ID"""
        return list(self.model.objects.filter(user_id=user_id).order_by("created_at"))

    def get_user_messages_by_role(self, user_id: int, role: str) -> List[Message]:
        """Get messages for a user filtered by role"""
        return list(
            self.model.objects.filter(user_id=user_id, role=role).order_by("created_at")
        )

    def get_recent_messages(self, user_id: int, limit: int = 10) -> List[Message]:
        """Get recent messages for a user"""
        return list(
            self.model.objects.filter(user_id=user_id).order_by("-created_at")[:limit]
        )

    def create_message(self, user_id: int, role: str, content: str) -> Message:
        """Create a new message"""
        return self.model.objects.create(user_id=user_id, role=role, content=content)

    def get_conversation_history(self, user_id: int) -> List[Message]:
        """Get complete conversation history for a user"""
        return list(self.model.objects.filter(user_id=user_id).order_by("created_at"))

    def delete_user_messages(self, user_id: int) -> int:
        """Delete all messages for a user"""
        count, _ = self.model.objects.filter(user_id=user_id).delete()
        return count

    def count_messages_by_user(self, user_id: int) -> int:
        """Count total messages for a user"""
        return self.model.objects.filter(user_id=user_id).count()

    def get_message_by_id_and_user(
        self, message_id: int, user_id: int
    ) -> Optional[Message]:
        """Get message by ID if it belongs to the specified user"""
        try:
            return self.model.objects.get(id=message_id, user_id=user_id)
        except self.model.DoesNotExist:
            return None

    def update_message_if_owner(
        self, message_id: int, user_id: int, **kwargs
    ) -> Optional[Message]:
        """Update message if user owns it"""
        try:
            message = self.model.objects.get(id=message_id, user_id=user_id)
            for key, value in kwargs.items():
                setattr(message, key, value)
            message.save()
            return message
        except self.model.DoesNotExist:
            return None

    def delete_message_if_owner(self, message_id: int, user_id: int) -> bool:
        """Delete message if user owns it"""
        try:
            message = self.model.objects.get(id=message_id, user_id=user_id)
            message.delete()
            return True
        except self.model.DoesNotExist:
            return False

    def create_conversation_pair(
        self, user_id: int, user_content: str, bot_content: str
    ) -> tuple:
        """
        Create both user and bot messages in a conversation pair
        Returns: (user_message, bot_message)
        """
        from django.db import transaction

        with transaction.atomic():
            # Create user message
            user_message = self.model.objects.create(
                user_id=user_id, role="user", content=user_content
            )

            # Create bot message
            bot_message = self.model.objects.create(
                user_id=user_id, role="bot", content=bot_content
            )

            return user_message, bot_message
