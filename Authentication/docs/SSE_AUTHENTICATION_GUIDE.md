# Server-Sent Events (SSE) Authentication System

## Overview

This document describes the Server-Sent Events (SSE) implementation for the single-device authentication system. The SSE mechanism provides real-time notifications to clients when authentication events occur, particularly when a user logs in from a new device and existing sessions need to be terminated.

## Architecture

### Components

1. **SSE Manager** (`sse_manager.py`)
   - Singleton class that manages active SSE connections
   - Maintains a registry of user connections
   - Handles event broadcasting to specific users

2. **SSE Views** (`sse_views.py`)
   - Provides the SSE endpoint for client connections
   - Handles authentication and authorization
   - Manages the event stream lifecycle

3. **Authentication Integration**
   - Login view triggers SSE events when new devices log in
   - Token refresh view notifies existing sessions of changes

### Flow Diagram

```
Client A                    Server                     Client B
   |                          |                          |
   |--- Login Request ------->|                          |
   |<-- Access Token ---------|                          |
   |                          |                          |
   |--- SSE Connection ------>|                          |
   |<-- Event Stream ---------|                          |
   |                          |                          |
   |                          |<--- Login Request -------|
   |                          |---- Access Token ------->|
   |                          |                          |
   |<-- FORCE_LOGOUT Event ---|                          |
   |                          |                          |
   |--- API Request --------->|                          |
   |<-- 401 Unauthorized -----|                          |
```

## Implementation Details

### SSE Manager

The `SSEManager` class is implemented as a singleton to ensure consistent state across the application:

```python
class SSEManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self.connections: Dict[int, Set[asyncio.Queue]] = {}
        self.connection_lock = Lock()
```

Key methods:
- `register_connection(user_id, queue)`: Registers a new SSE connection for a user
- `remove_connection(user_id, queue)`: Removes an SSE connection
- `send_event(user_id, event_type, data)`: Sends an event to all connections for a user

### SSE Endpoint

The SSE endpoint is implemented as a Django REST Framework view:

```python
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([SingleDeviceJWTAuthentication])
def sse_notifications(request):
    """SSE endpoint for user notifications"""
    response = StreamingHttpResponse(
        event_stream(request), content_type="text/event-stream"
    )
    
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    response["Connection"] = "keep-alive"
    
    return response
```

### Event Stream Generator

The event stream is implemented as an async generator:

```python
async def event_stream(request) -> AsyncGenerator[str, None]:
    user_id = request.user.id
    queue = asyncio.Queue()
    sse_manager.register_connection(user_id, queue)

    try:
        while True:
            try:
                # Send heartbeat every 30 seconds
                yield "event: heartbeat\ndata: {}\n\n"
                
                # Wait for events with timeout
                message = await asyncio.wait_for(queue.get(), timeout=30)
                yield f"event: message\ndata: {message}\n\n"
            except asyncio.TimeoutError:
                pass  # Continue with heartbeat
    except asyncio.CancelledError:
        pass  # Connection closed
    finally:
        sse_manager.remove_connection(user_id, queue)
```

## Event Types

### FORCE_LOGOUT

Sent when a user logs in from a new device, forcing existing sessions to terminate.

**Event Format:**
```javascript
{
  "type": "FORCE_LOGOUT",
  "data": {
    "message": "Your account was logged in from another device."
  }
}
```

**Client Handling:**
```javascript
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'FORCE_LOGOUT') {
        alert(data.data.message);
        // Redirect to login page or clear local storage
        logout();
    }
};
```

### Heartbeat

Sent every 30 seconds to keep the connection alive.

**Event Format:**
```javascript
{
  "type": "heartbeat",
  "data": {}
}
```

## Security Considerations

1. **Authentication Required**: All SSE connections must be authenticated using valid JWT tokens
2. **User Isolation**: Events are only sent to the specific user who should receive them
3. **Connection Cleanup**: Connections are properly cleaned up when clients disconnect
4. **Rate Limiting**: Consider implementing rate limiting for SSE connections

## Configuration

### Django Settings

Ensure the following settings are configured:

```python
# settings.py
INSTALLED_APPS = [
    'channels',  # Required for async support
    # ... other apps
]

ASGI_APPLICATION = "YourProject.asgi.application"

# Channel layers configuration (if using Redis)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

### URL Configuration

```python
# urls.py
from Authentication.sse_views import sse_notifications

urlpatterns = [
    path("sse/notifications/", sse_notifications, name="sse_notifications"),
    # ... other URLs
]
```

## Testing

The SSE system includes comprehensive tests covering:

1. **SSE Manager Tests**
   - Connection registration and removal
   - Event broadcasting
   - Logout notifications

2. **SSE View Tests**
   - Authentication requirements
   - Response headers
   - Stream content format

3. **Integration Tests**
   - End-to-end login flow
   - Force logout functionality
   - Token invalidation

Run tests with:
```bash
python manage.py test Authentication.tests.test_sse
```

## Deployment Considerations

### Production Environment

1. **ASGI Server**: Use an ASGI server like Uvicorn or Daphne to handle async requests
2. **Load Balancing**: Consider sticky sessions if using multiple server instances
3. **Connection Limits**: Monitor and limit concurrent SSE connections
4. **Redis**: Use Redis for channel layers in production

### Docker Configuration

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    command: daphne -b 0.0.0.0 -p 8000 YourProject.asgi:application
    
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## Troubleshooting

### Common Issues

1. **Connection Not Established**
   - Check authentication token validity
   - Verify CORS settings for cross-origin requests
   - Ensure ASGI server is running

2. **Events Not Received**
   - Check SSE manager connection registry
   - Verify event broadcasting logic
   - Monitor server logs for errors

3. **Memory Leaks**
   - Ensure connections are properly cleaned up
   - Monitor connection count over time
   - Check for orphaned queue objects

### Debugging

Enable debug logging:
```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'Authentication.sse_views': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Performance Considerations

1. **Connection Limits**: Monitor concurrent SSE connections
2. **Memory Usage**: Each connection maintains a queue in memory
3. **Heartbeat Frequency**: Balance between connection reliability and server load
4. **Event Batching**: Consider batching multiple events if needed

## Future Enhancements

1. **Event Persistence**: Store events for offline clients
2. **Event Filtering**: Allow clients to subscribe to specific event types
3. **Connection Analytics**: Track connection metrics and user behavior
4. **Scalability**: Implement horizontal scaling with message queues
