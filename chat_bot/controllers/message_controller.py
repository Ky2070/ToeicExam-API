from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..services.message_service import MessageService
from ..serializers import (
    MessageSerializer,
    MessageCreateSerializer,
    ConversationCreateSerializer,
    ConversationResponseSerializer,
)


# Initialize service
message_service = MessageService()


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_messages(request):
    """GET /messages/ - Get user's messages, POST /messages/ - Create new message for authenticated user"""
    user_id = request.user.id

    if request.method == "GET":
        try:
            result = message_service.get_user_messages(user_id)

            if result["success"]:
                serializer = MessageSerializer(result["messages"], many=True)
                return Response(
                    {
                        "success": True,
                        "data": serializer.data,
                        "count": len(result["messages"]),
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"success": False, "errors": result["errors"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    elif request.method == "POST":
        try:
            serializer = ConversationCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"success": False, "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            content = serializer.validated_data["content"]

            # Create conversation (user message + bot response)
            result = message_service.create_conversation(user_id, content)

            if result["success"]:
                # Serialize both messages
                response_data = {
                    "user_message": MessageSerializer(result["user_message"]).data,
                    "bot_message": MessageSerializer(result["bot_message"]).data,
                }

                return Response(
                    {
                        "success": True,
                        "data": response_data,
                        "message": "Conversation created successfully",
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"success": False, "errors": result["errors"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def message_detail(request, message_id):
    """GET /messages/{id}/ - Get message, PUT /messages/{id}/ - Update message, DELETE /messages/{id}/ - Delete message"""
    user_id = request.user.id

    if request.method == "GET":
        try:
            result = message_service.get_message_by_id_for_user(message_id, user_id)

            if result["success"]:
                serializer = MessageSerializer(result["message"])
                return Response(
                    {"success": True, "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"success": False, "errors": result["errors"]},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    elif request.method == "PUT":
        try:
            # Validate input data
            serializer = MessageCreateSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(
                    {"success": False, "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract fields to update
            role = serializer.validated_data.get("role")
            content = serializer.validated_data.get("content")

            result = message_service.update_message_for_user(
                message_id, user_id, role, content
            )

            if result["success"]:
                response_serializer = MessageSerializer(result["message"])
                return Response(
                    {
                        "success": True,
                        "data": response_serializer.data,
                        "message": "Message updated successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"success": False, "errors": result["errors"]},
                    status=status.HTTP_403_FORBIDDEN,
                )

        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    elif request.method == "DELETE":
        try:
            result = message_service.delete_message_for_user(message_id, user_id)

            if result["success"]:
                return Response(
                    {"success": True, "message": "Message deleted successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"success": False, "errors": result["errors"]},
                    status=status.HTTP_403_FORBIDDEN,
                )

        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def conversation_history(request):
    """GET /messages/history/ - Get conversation history for authenticated user"""
    user_id = request.user.id

    try:
        # Get optional limit parameter
        limit = request.GET.get("limit")
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                return Response(
                    {"success": False, "error": "Invalid limit parameter"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        result = message_service.get_conversation_history(user_id, limit)

        if result["success"]:
            serializer = MessageSerializer(result["messages"], many=True)
            return Response(
                {
                    "success": True,
                    "data": serializer.data,
                    "count": len(result["messages"]),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"success": False, "errors": result["errors"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def clear_conversation(request):
    """DELETE /messages/clear/ - Delete all messages for authenticated user"""
    user_id = request.user.id

    try:
        result = message_service.delete_user_conversation(user_id)

        if result["success"]:
            return Response(
                {
                    "success": True,
                    "message": f"Deleted {result['count']} messages successfully",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"success": False, "errors": result["errors"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def messages_by_role(request):
    """GET /messages/by-role/ - Get messages filtered by role for authenticated user"""
    user_id = request.user.id

    try:
        role = request.GET.get("role")
        if not role:
            return Response(
                {"success": False, "error": "Role parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = message_service.get_messages_by_role(user_id, role)

        if result["success"]:
            serializer = MessageSerializer(result["messages"], many=True)
            return Response(
                {
                    "success": True,
                    "data": serializer.data,
                    "count": len(result["messages"]),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"success": False, "errors": result["errors"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def message_count(request):
    """GET /messages/count/ - Get total message count for authenticated user"""
    user_id = request.user.id

    try:
        result = message_service.get_message_count(user_id)

        if result["success"]:
            return Response(
                {"success": True, "count": result["count"]}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"success": False, "errors": result["errors"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
