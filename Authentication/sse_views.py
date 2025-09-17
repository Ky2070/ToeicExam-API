import asyncio
import json
from typing import AsyncGenerator
from django.http import StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import AnonymousUser
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .authentication import SingleDeviceJWTAuthentication
from .sse_manager import sse_manager


def authenticate_sse_request(request):
    """
    Custom authentication for SSE requests.
    Returns the authenticated user or None if authentication fails.

    Supports multiple authentication methods:
    1. JWT token in Authorization header
    2. JWT token in query parameter 'token'
    3. Session authentication (fallback)
    """
    # Method 1: Try JWT authentication from Authorization header
    jwt_auth = SingleDeviceJWTAuthentication()
    try:
        auth_result = jwt_auth.authenticate(request)
        if auth_result:
            user, token = auth_result
            return user
    except (InvalidToken, TokenError):
        pass

    # Method 2: Try JWT token from query parameter
    token = request.GET.get("token")
    if token:
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            from django.contrib.auth import get_user_model

            # Validate the token
            access_token = AccessToken(token)
            user_id = access_token["user_id"]

            # Get user and validate JTI (single device enforcement)
            User = get_user_model()
            user = User.objects.get(id=user_id)

            # Check if token JTI matches user's current JTI
            token_jti = access_token.get("jti")
            if user.current_jti and token_jti != user.current_jti:
                return None  # Token is from old device

            return user

        except (InvalidToken, TokenError, User.DoesNotExist, Exception):
            pass

    # Method 3: Try session authentication as fallback
    if hasattr(request, "user") and request.user.is_authenticated:
        return request.user

    return None


async def event_stream(request) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events stream for the authenticated user.

    This async generator maintains a connection with the client and sends:
    1. Heartbeat events every 30 seconds to keep connection alive
    2. Real-time notifications (like FORCE_LOGOUT) when they occur
    """
    user_id = request.user.id
    queue = asyncio.Queue()

    # Register this connection with the SSE manager
    sse_manager.register_connection(user_id, queue)

    try:
        while True:
            try:
                # Wait for events from the queue with a timeout
                message = await asyncio.wait_for(queue.get(), timeout=30)
                yield f"event: message\ndata: {message}\n\n"
            except asyncio.TimeoutError:
                # Send heartbeat every 30 seconds to keep connection alive
                yield "event: heartbeat\ndata: {}\n\n"
            except asyncio.CancelledError:
                # Connection was cancelled/closed
                break
            except Exception:
                # Handle other exceptions gracefully
                break
    finally:
        # Clean up the connection when the client disconnects
        sse_manager.remove_connection(user_id, queue)


@csrf_exempt
@require_http_methods(["GET"])
def sse_notifications(request):
    """
    SSE endpoint for user notifications.

    This view bypasses DRF's content negotiation to return proper SSE responses.
    It manually handles authentication and returns StreamingHttpResponse.

    This fixes the "Could not satisfy the request Accept header" error by:
    1. Not using DRF decorators that enforce JSON content negotiation
    2. Manually handling authentication
    3. Returning proper StreamingHttpResponse with text/event-stream content type
    """
    # Authenticate the request
    user = authenticate_sse_request(request)
    if not user:
        # Return 401 with proper SSE format
        def error_stream():
            yield 'event: error\ndata: {"error": "Authentication required"}\n\n'

        response = StreamingHttpResponse(
            error_stream(), content_type="text/event-stream", status=401
        )
        response["Cache-Control"] = "no-cache"
        # Don't set Connection header - WSGI handles this
        return response

    # Set the authenticated user on the request
    request.user = user

    # Create the SSE response
    response = StreamingHttpResponse(
        event_stream(request), content_type="text/event-stream"
    )

    # Set required SSE headers
    response["Cache-Control"] = "no-cache"
    # Don't set Connection header - WSGI/Django handles this automatically
    response["X-Accel-Buffering"] = "no"  # Disable nginx buffering

    # CORS headers (adjust as needed for your frontend)
    response["Access-Control-Allow-Origin"] = (
        "*"  # Change to your frontend URL in production
    )
    response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    response["Access-Control-Allow-Methods"] = "GET"
    response["Access-Control-Allow-Credentials"] = "true"

    return response


# Alternative: Simple test endpoint for debugging SSE connectivity
@csrf_exempt
def sse_test(request):
    """
    Simple SSE test endpoint without authentication.
    Useful for testing SSE connectivity and debugging frontend issues.

    Usage: GET /api/v1/auth/sse/test/
    """

    def simple_stream():
        import time

        for i in range(10):
            yield f"data: Test message {i} at {time.strftime('%H:%M:%S')}\n\n"
            time.sleep(2)
        yield "data: Stream completed\n\n"

    response = StreamingHttpResponse(simple_stream(), content_type="text/event-stream")

    response["Cache-Control"] = "no-cache"
    # Don't set Connection header - WSGI handles this
    response["Access-Control-Allow-Origin"] = "*"

    return response


@csrf_exempt
@require_http_methods(["GET"])
def sse_notifications_sync(request):
    """
    Synchronous version of SSE notifications for testing with Django dev server.

    The async version might not work well with Django's development server,
    so this provides a synchronous alternative for testing.
    """
    # Authenticate the request
    user = authenticate_sse_request(request)
    if not user:

        def error_stream():
            yield 'event: error\ndata: {"error": "Authentication required"}\n\n'

        response = StreamingHttpResponse(
            error_stream(), content_type="text/event-stream", status=401
        )
        response["Cache-Control"] = "no-cache"
        return response

    # Set the authenticated user on the request
    request.user = user

    def sync_event_stream():
        """Synchronous event stream generator"""
        import time
        import json

        # Send initial connection message
        yield f'event: connected\ndata: {{"user_id": {user.id}, "message": "Connected successfully"}}\n\n'

        # Send heartbeats and check for messages
        for i in range(60):  # Run for 60 iterations (about 2 minutes with 2s intervals)
            try:
                # In a real implementation, you'd check the SSE manager for messages
                # For now, just send periodic heartbeats
                if i % 15 == 0:  # Every 30 seconds (15 * 2s)
                    yield "event: heartbeat\ndata: {}\n\n"
                else:
                    yield 'event: ping\ndata: {"timestamp": "' + time.strftime(
                        "%H:%M:%S"
                    ) + '"}\n\n'

                time.sleep(2)  # Wait 2 seconds between messages

            except Exception as e:
                yield f'event: error\ndata: {{"error": "Stream error: {str(e)}"}}\n\n'
                break

        yield 'event: end\ndata: {"message": "Stream ended"}\n\n'

    # Create the SSE response
    response = StreamingHttpResponse(
        sync_event_stream(), content_type="text/event-stream"
    )

    # Set required SSE headers
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"

    # CORS headers
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    response["Access-Control-Allow-Methods"] = "GET"
    response["Access-Control-Allow-Credentials"] = "true"

    return response


# DRF-compatible view (alternative approach - may still have issues with some DRF versions)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([SingleDeviceJWTAuthentication])
def sse_notifications_drf(request):
    """
    DRF-compatible SSE endpoint.

    Note: This might still have the "Could not satisfy the request Accept header" error
    with some DRF versions due to content negotiation. Use sse_notifications above instead.
    """
    response = StreamingHttpResponse(
        event_stream(request), content_type="text/event-stream"
    )

    response["Cache-Control"] = "no-cache"
    # Don't set Connection header - WSGI handles this
    response["X-Accel-Buffering"] = "no"

    return response


async def notify_logout(user_id: int):
    """Send force logout notification to all user's connections"""
    await sse_manager.send_event(
        user_id,
        "FORCE_LOGOUT",
        {"message": "Your account was logged in from another device."},
    )
