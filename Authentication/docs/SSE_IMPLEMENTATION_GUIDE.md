# Server-Sent Events (SSE) Implementation Guide

## Problem: "Could not satisfy the request Accept header" Error

When implementing Server-Sent Events (SSE) with Django REST Framework, you might encounter this error:

```
detail: "Could not satisfy the request Accept header."
```

This happens because:
1. DRF expects `application/json` content type by default
2. SSE requires `text/event-stream` content type
3. DRF's content negotiation conflicts with SSE requirements

## Solution Overview

We'll create a **non-DRF view** that bypasses content negotiation while still supporting authentication.

## Backend Implementation

### 1. SSE Views (`sse_views.py`)

The key is to use Django's `StreamingHttpResponse` directly instead of DRF's `Response`:

```python
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["GET"])
def sse_notifications(request):
    """
    SSE endpoint that fixes the Accept header error.
    
    This view bypasses DRF's content negotiation by:
    1. Not using DRF decorators
    2. Manually handling authentication
    3. Returning StreamingHttpResponse with proper content type
    """
    # Manual authentication
    user = authenticate_sse_request(request)
    if not user:
        def error_stream():
            yield 'event: error\ndata: {"error": "Authentication required"}\n\n'
        
        return StreamingHttpResponse(
            error_stream(),
            content_type="text/event-stream",
            status=401
        )
    
    request.user = user
    
    # Create SSE response
    response = StreamingHttpResponse(
        event_stream(request),
        content_type="text/event-stream"  # This fixes the Accept header error
    )
    
    # Required SSE headers
    response["Cache-Control"] = "no-cache"
    response["Connection"] = "keep-alive"
    response["X-Accel-Buffering"] = "no"
    
    # CORS headers (adjust for your frontend)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    response["Access-Control-Allow-Methods"] = "GET"
    
    return response
```

### 2. Authentication Helper

```python
def authenticate_sse_request(request):
    """Custom authentication for SSE requests"""
    # Try JWT authentication
    jwt_auth = SingleDeviceJWTAuthentication()
    try:
        auth_result = jwt_auth.authenticate(request)
        if auth_result:
            user, token = auth_result
            return user
    except (InvalidToken, TokenError):
        pass
    
    # Fallback to session authentication
    if hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    
    return None
```

### 3. Event Stream Generator

```python
async def event_stream(request):
    """Generate SSE events"""
    user_id = request.user.id
    queue = asyncio.Queue()
    
    # Register connection
    sse_manager.register_connection(user_id, queue)
    
    try:
        while True:
            try:
                # Wait for events with 30s timeout
                message = await asyncio.wait_for(queue.get(), timeout=30)
                yield f"event: message\ndata: {message}\n\n"
            except asyncio.TimeoutError:
                # Send heartbeat
                yield "event: heartbeat\ndata: {}\n\n"
    finally:
        sse_manager.remove_connection(user_id, queue)
```

### 4. URL Configuration

```python
# urls.py
from .sse_views import sse_notifications, sse_test

urlpatterns = [
    # ... other URLs
    path("sse/notifications/", sse_notifications, name="sse_notifications"),
    path("sse/test/", sse_test, name="sse_test"),  # For testing
]
```

## Frontend Implementation (React)

### 1. Basic EventSource Connection

```javascript
// Basic connection
const eventSource = new EventSource('http://localhost:8000/api/v1/auth/sse/notifications/');

eventSource.onopen = () => {
    console.log('SSE connection opened');
};

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    
    if (data.type === 'FORCE_LOGOUT') {
        alert(data.data.message);
        // Handle logout
    }
};

eventSource.onerror = (error) => {
    console.error('SSE error:', error);
};
```

### 2. Authentication with EventSource

**Problem**: EventSource doesn't support custom headers (like Authorization).

**Solutions**:

#### Option A: Query Parameter (Recommended)
```python
# Backend: Accept token as query parameter
def sse_notifications(request):
    token = request.GET.get('token')
    if token:
        # Validate token manually
        user = validate_jwt_token(token)
    # ...
```

```javascript
// Frontend: Pass token as query parameter
const eventSource = new EventSource(
    `http://localhost:8000/api/v1/auth/sse/notifications/?token=${encodeURIComponent(accessToken)}`
);
```

#### Option B: Cookie-based Authentication
```python
# Backend: Use session authentication
@csrf_exempt
def sse_notifications(request):
    if request.user.is_authenticated:
        # User is authenticated via session
        pass
```

```javascript
// Frontend: Ensure cookies are sent
const eventSource = new EventSource(
    'http://localhost:8000/api/v1/auth/sse/notifications/',
    { withCredentials: true }
);
```

### 3. React Hook for SSE

```javascript
const useSSE = (url, accessToken, options = {}) => {
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState(null);
    const [error, setError] = useState(null);
    const eventSourceRef = useRef(null);

    const connect = useCallback(() => {
        if (!accessToken) return;

        const eventSource = new EventSource(`${url}?token=${encodeURIComponent(accessToken)}`);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
            setIsConnected(true);
            setError(null);
        };

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setLastMessage(data);
            options.onMessage?.(data);
        };

        eventSource.onerror = (error) => {
            setIsConnected(false);
            setError('Connection error');
            options.onError?.(error);
        };
    }, [url, accessToken, options]);

    useEffect(() => {
        if (accessToken) {
            connect();
        }
        return () => {
            eventSourceRef.current?.close();
        };
    }, [accessToken, connect]);

    return { isConnected, lastMessage, error };
};
```

### 4. Complete React Component

```javascript
const SSEManager = () => {
    const { accessToken, logout } = useAuth();
    
    const handleMessage = (data) => {
        if (data.type === 'FORCE_LOGOUT') {
            alert(data.data.message);
            logout();
        }
    };

    const { isConnected, error } = useSSE(
        'http://localhost:8000/api/v1/auth/sse/notifications/',
        accessToken,
        { onMessage: handleMessage }
    );

    return (
        <div>
            Status: {isConnected ? 'Connected' : 'Disconnected'}
            {error && <span>Error: {error}</span>}
        </div>
    );
};
```

## Testing the Implementation

### 1. Test SSE Connectivity

First, test with the simple endpoint:

```bash
curl -N http://localhost:8000/api/v1/auth/sse/test/
```

Expected output:
```
data: Test message 0 at 14:30:15

data: Test message 1 at 14:30:17

...
```

### 2. Test with Authentication

```bash
# Get access token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}' | \
  jq -r '.access')

# Test SSE with token
curl -N "http://localhost:8000/api/v1/auth/sse/notifications/?token=$TOKEN"
```

### 3. Frontend Testing

```javascript
// Test component for debugging
const SSETest = () => {
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        const eventSource = new EventSource('http://localhost:8000/api/v1/auth/sse/test/');
        
        eventSource.onmessage = (event) => {
            setMessages(prev => [...prev, event.data]);
        };

        return () => eventSource.close();
    }, []);

    return (
        <div>
            <h3>SSE Test</h3>
            {messages.map((msg, i) => <div key={i}>{msg}</div>)}
        </div>
    );
};
```

## Common Issues and Solutions

### 1. "Could not satisfy the request Accept header"

**Cause**: Using DRF decorators that enforce JSON content negotiation.

**Solution**: Use plain Django views with `StreamingHttpResponse`.

### 2. CORS Errors

**Cause**: Frontend and backend on different origins.

**Solution**: Add CORS headers to SSE response:
```python
response["Access-Control-Allow-Origin"] = "http://localhost:3000"
response["Access-Control-Allow-Credentials"] = "true"
```

### 3. Connection Drops

**Cause**: Proxy servers or browsers closing idle connections.

**Solution**: Send regular heartbeats:
```python
# Send heartbeat every 30 seconds
except asyncio.TimeoutError:
    yield "event: heartbeat\ndata: {}\n\n"
```

### 4. Authentication Issues

**Cause**: EventSource doesn't support Authorization headers.

**Solutions**:
- Use query parameters for tokens
- Use cookie-based authentication
- Consider WebSockets for more complex auth

### 5. Memory Leaks

**Cause**: Not cleaning up SSE connections.

**Solution**: Proper cleanup in finally block:
```python
finally:
    sse_manager.remove_connection(user_id, queue)
```

## Production Considerations

### 1. Nginx Configuration

```nginx
# Special handling for SSE endpoints
location /api/v1/auth/sse/ {
    proxy_pass http://django;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 24h;
}
```

### 2. Connection Limits

```python
# Limit concurrent connections per user
MAX_CONNECTIONS_PER_USER = 5

def register_connection(self, user_id, queue):
    if len(self.connections.get(user_id, [])) >= MAX_CONNECTIONS_PER_USER:
        raise Exception("Too many connections")
    # ... register connection
```

### 3. Monitoring

```python
# Add logging for SSE connections
import logging

logger = logging.getLogger(__name__)

def register_connection(self, user_id, queue):
    logger.info(f"SSE connection registered for user {user_id}")
    # ... register connection
```

## Alternative: WebSocket Implementation

If SSE limitations become problematic, consider WebSockets:

```python
# WebSocket consumer (using Django Channels)
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Authenticate user
        user = await self.get_user()
        if user:
            await self.accept()
            await self.channel_layer.group_add(f"user_{user.id}", self.channel_name)
        else:
            await self.close(code=4001)  # Unauthorized

    async def disconnect(self, close_code):
        if hasattr(self, 'user'):
            await self.channel_layer.group_discard(f"user_{self.user.id}", self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event['message']))
```

```javascript
// WebSocket client
const ws = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${accessToken}`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Handle message
};
```

## Summary

The key to fixing the "Could not satisfy the request Accept header" error is:

1. **Bypass DRF**: Use plain Django views instead of DRF decorators
2. **Manual Auth**: Handle authentication manually in the view
3. **Proper Headers**: Return `StreamingHttpResponse` with `text/event-stream`
4. **Token Handling**: Pass JWT tokens as query parameters (EventSource limitation)
5. **Error Handling**: Implement proper reconnection and error handling

This approach gives you full control over the SSE implementation while maintaining compatibility with your existing authentication system.
