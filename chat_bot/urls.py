from django.urls import path
from .controllers import message_controller, history_controller

app_name = "chat_bot"

urlpatterns = [
    # Message endpoints for authenticated users
    path(
        "messages/", message_controller.user_messages, name="user_messages"
    ),  # GET /messages/, POST /messages/
    path(
        "messages/<int:message_id>/",
        message_controller.message_detail,
        name="message_detail",
    ),  # GET /messages/{id}/, PUT /messages/{id}/, DELETE /messages/{id}/
    # Additional utility endpoints
    path(
        "messages/history/",
        message_controller.conversation_history,
        name="conversation_history",
    ),  # GET /messages/history/
    path(
        "messages/clear/",
        message_controller.clear_conversation,
        name="clear_conversation",
    ),  # DELETE /messages/clear/
    path(
        "messages/by-role/",
        message_controller.messages_by_role,
        name="messages_by_role",
    ),  # GET /messages/by-role/
    path(
        "messages/count/", message_controller.message_count, name="message_count"
    ),  # GET /messages/count/
    # path(
    #     "history/latest/", history_controller.get_latest_results, name="history_score"
    # ),
]
