from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""

    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "user", "user_username", "role", "content", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_role(self, value):
        """Validate message role"""
        valid_roles = ["user", "bot", "system"]
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Role must be one of: {', '.join(valid_roles)}"
            )
        return value


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages (without user field in input)"""

    class Meta:
        model = Message
        fields = ["role", "content"]

    def validate_role(self, value):
        """Validate message role"""
        valid_roles = ["user", "bot", "system"]
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Role must be one of: {', '.join(valid_roles)}"
            )
        return value


class ConversationCreateSerializer(serializers.Serializer):
    """Serializer for creating a conversation (user message only)"""

    content = serializers.CharField(max_length=10000)

    def validate_content(self, value):
        """Validate message content"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Content cannot be empty")
        return value.strip()


class ConversationResponseSerializer(serializers.Serializer):
    """Serializer for conversation response (user + bot messages)"""

    user_message = MessageSerializer()
    bot_message = MessageSerializer()

    class Meta:
        fields = ["user_message", "bot_message"]
