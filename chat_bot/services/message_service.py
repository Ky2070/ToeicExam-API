from typing import List, Optional, Dict, Any, Tuple
from ..models import Message
from ..repositories.message_repository import MessageRepository
from .bot_service import BotService
from django.contrib.auth import get_user_model
User = get_user_model()

class MessageService:
    """Service layer for Message business logic"""

    def __init__(self):
        self.message_repository = MessageRepository()
        self.bot_service = BotService()

    def get_user_messages(self, user_id: int) -> Dict[str, Any]:
        """
        Get all messages for a specific user
        Returns: Dict with 'success', 'messages', and 'errors' keys
        """
        try:
            messages = self.message_repository.get_by_user_id(user_id)
            return {"success": True, "messages": messages, "errors": []}
        except Exception as e:
            return {"success": False, "messages": [], "errors": [str(e)]}

    def create_message(self, user_id: int, role: str, content: str) -> Dict[str, Any]:
        """
        Create a new message with validation
        Returns: Dict with 'success', 'message', and 'errors' keys
        """
        errors = self._validate_message_data(role, content)
        if errors:
            return {"success": False, "message": None, "errors": errors}

        try:
            message = self.message_repository.create_message(user_id, role, content)
            return {"success": True, "message": message, "errors": []}
        except Exception as e:
            return {"success": False, "message": None, "errors": [str(e)]}

    def get_message_by_id_for_user(
        self, message_id: int, user_id: int
    ) -> Dict[str, Any]:
        """
        Get message by ID if it belongs to the user
        Returns: Dict with 'success', 'message', and 'errors' keys
        """
        try:
            message = self.message_repository.get_message_by_id_and_user(
                message_id, user_id
            )
            if not message:
                return {
                    "success": False,
                    "message": None,
                    "errors": ["Message not found or access denied"],
                }
            return {"success": True, "message": message, "errors": []}
        except Exception as e:
            return {"success": False, "message": None, "errors": [str(e)]}

    def update_message_for_user(
        self, message_id: int, user_id: int, role: str = None, content: str = None
    ) -> Dict[str, Any]:
        """
        Update message if it belongs to the user
        Returns: Dict with 'success', 'message', and 'errors' keys
        """
        # Validate new data if provided
        errors = []
        if role and role not in ["user", "bot", "system"]:
            errors.append("Role must be one of: user, bot, system")

        if content is not None and len(content.strip()) == 0:
            errors.append("Content cannot be empty")

        if errors:
            return {"success": False, "message": None, "errors": errors}

        try:
            update_data = {}
            if role:
                update_data["role"] = role
            if content is not None:
                update_data["content"] = content

            updated_message = self.message_repository.update_message_if_owner(
                message_id, user_id, **update_data
            )
            if not updated_message:
                return {
                    "success": False,
                    "message": None,
                    "errors": ["Message not found or access denied"],
                }

            return {"success": True, "message": updated_message, "errors": []}
        except Exception as e:
            return {"success": False, "message": None, "errors": [str(e)]}

    def delete_message_for_user(self, message_id: int, user_id: int) -> Dict[str, Any]:
        """
        Delete message if it belongs to the user
        Returns: Dict with 'success' and 'errors' keys
        """
        try:
            success = self.message_repository.delete_message_if_owner(
                message_id, user_id
            )
            if success:
                return {"success": True, "errors": []}
            else:
                return {
                    "success": False,
                    "errors": ["Message not found or access denied"],
                }
        except Exception as e:
            return {"success": False, "errors": [str(e)]}

    def get_conversation_history(
        self, user_id: int, limit: int = None
    ) -> Dict[str, Any]:
        """
        Get conversation history for a user
        Returns: Dict with 'success', 'messages', and 'errors' keys
        """
        try:
            if limit:
                messages = self.message_repository.get_recent_messages(user_id, limit)
                messages.reverse()  # Reverse to get chronological order
            else:
                messages = self.message_repository.get_conversation_history(user_id)

            return {"success": True, "messages": messages, "errors": []}
        except Exception as e:
            return {"success": False, "messages": [], "errors": [str(e)]}

    def get_messages_by_role(self, user_id: int, role: str) -> Dict[str, Any]:
        """
        Get messages for a user filtered by role
        Returns: Dict with 'success', 'messages', and 'errors' keys
        """
        if role not in ["user", "bot", "system"]:
            return {"success": False, "messages": [], "errors": ["Invalid role"]}

        try:
            messages = self.message_repository.get_user_messages_by_role(user_id, role)
            return {"success": True, "messages": messages, "errors": []}
        except Exception as e:
            return {"success": False, "messages": [], "errors": [str(e)]}

    def delete_user_conversation(self, user_id: int) -> Dict[str, Any]:
        """
        Delete all messages for a user
        Returns: Dict with 'success', 'count', and 'errors' keys
        """
        try:
            count = self.message_repository.delete_user_messages(user_id)
            return {"success": True, "count": count, "errors": []}
        except Exception as e:
            return {"success": False, "count": 0, "errors": [str(e)]}

    def get_message_count(self, user_id: int) -> Dict[str, Any]:
        """
        Get total message count for a user
        Returns: Dict with 'success', 'count', and 'errors' keys
        """
        try:
            count = self.message_repository.count_messages_by_user(user_id)
            return {"success": True, "count": count, "errors": []}
        except Exception as e:
            return {"success": False, "count": 0, "errors": [str(e)]}

    def _validate_message_data(self, role: str, content: str) -> List[str]:
        """Validate message input data"""
        errors = []

        # Role validation
        if role not in ["user", "bot", "system"]:
            errors.append("Role must be one of: user, bot, system")

        # Content validation
        if not content or len(content.strip()) == 0:
            errors.append("Content cannot be empty")

        if len(content) > 10000:  # Reasonable limit for message content
            errors.append("Content must be 10000 characters or less")

        return errors

    def create_conversation(self, user: User, user_content: str) -> Dict[str, Any]:
        """
        Create a conversation by saving user message and generating bot response
        """
        errors = self._validate_message_data("user", user_content)
        if errors:
            return {
                "success": False,
                "user_message": None,
                "bot_message": None,
                "errors": errors,
            }

        try:
            # Lấy lịch sử hội thoại gần nhất
            recent_messages = self.message_repository.get_recent_messages(
                user.id, limit=5
            )
            conversation_history = [
                {"role": msg.role, "content": msg.content} for msg in recent_messages
            ]

            # Gọi bot, truyền luôn user để check role
            bot_response = self.bot_service.generate_response(
                user=user,
                user_message=user_content,
                conversation_history=conversation_history
            )

            # Lưu 2 tin nhắn
            user_message, bot_message = self.message_repository.create_conversation_pair(
                user.id, user_content, bot_response
            )

            return {
                "success": True,
                "user_message": user_message,
                "bot_message": bot_message,
                "errors": [],
            }

        except Exception as e:
            return {
                "success": False,
                "user_message": None,
                "bot_message": None,
                "errors": [str(e)],
            }
