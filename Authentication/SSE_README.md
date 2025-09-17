# Server-Sent Events (SSE) Implementation

## Quick Start

### Backend Setup

1. **SSE Endpoints are ready** at:
   - `/api/v1/auth/sse/notifications/` - Authenticated SSE endpoint
   - `/api/v1/auth/sse/test/` - Simple test endpoint (no auth required)

2. **Authentication Methods Supported**:
   - JWT token in Authorization header: `Authorization: Bearer <token>`
   - JWT token as query parameter: `?token=<token>`
   - Session-based authentication (cookies)

### Frontend Usage (React)

```javascript
// Basic connection with token
const eventSource = new EventSource(
  `http://localhost:8000/api/v1/auth/sse/notifications/?token=${accessToken}`
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'FORCE_LOGOUT') {
    alert(data.data.message);
    logout();
  }
};
```

### Testing

1. **Test simple SSE (no auth)**:
   ```bash
   curl -N http://localhost:8000/api/v1/auth/sse/test/
   ```

2. **Test authenticated SSE**:
   ```bash
   # Login first
   TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password"}' | \
     jq -r '.access')

   # Connect to SSE
   curl -N "http://localhost:8000/api/v1/auth/sse/notifications/?token=$TOKEN"
   ```

3. **Use Python test client**:
   ```bash
   pip install aiohttp
   python Authentication/test_sse_client.py --test-auth --email user@example.com --password password123
   ```

## Key Features

✅ **Fixed "Could not satisfy the request Accept header" error**
- Uses Django's `StreamingHttpResponse` instead of DRF's `Response`
- Bypasses DRF content negotiation
- Returns proper `text/event-stream` content type

✅ **Multiple Authentication Methods**
- JWT tokens via query parameters (recommended for EventSource)
- JWT tokens via Authorization header (for custom clients)
- Session-based authentication (fallback)

✅ **Single-Device Enforcement**
- Validates JWT `jti` against user's `current_jti`
- Sends `FORCE_LOGOUT` events when user logs in from new device

✅ **Production Ready**
- Proper error handling and cleanup
- CORS support
- Connection management
- Heartbeat mechanism

## Files Created/Updated

### Backend
- `Authentication/sse_views.py` - SSE endpoint implementations
- `Authentication/sse_manager.py` - Connection management
- `Authentication/urls.py` - URL routing
- `Authentication/test_sse_client.py` - Python test client

### Frontend Examples
- `Authentication/examples/react_sse_client.jsx` - Complete React implementation
- `Authentication/examples/sse_client.js` - Vanilla JavaScript client

### Documentation
- `Authentication/docs/SSE_IMPLEMENTATION_GUIDE.md` - Complete implementation guide
- `Authentication/docs/SSE_AUTHENTICATION_GUIDE.md` - Technical details
- `Authentication/docs/API_ENDPOINTS.md` - API documentation
- `Authentication/docs/DEPLOYMENT_GUIDE.md` - Production deployment

## Common Issues Solved

1. **"Could not satisfy the request Accept header"** ✅
   - Solution: Use plain Django views instead of DRF decorators

2. **EventSource doesn't support Authorization headers** ✅
   - Solution: Pass JWT token as query parameter

3. **CORS issues with SSE** ✅
   - Solution: Proper CORS headers in SSE response

4. **Connection cleanup and memory leaks** ✅
   - Solution: Proper cleanup in `finally` blocks

5. **Authentication with EventSource** ✅
   - Solution: Multiple auth methods including query parameters

## Next Steps

1. **Test the implementation** with your React frontend
2. **Adjust CORS settings** for your production domain
3. **Configure Nginx** for SSE if using reverse proxy
4. **Monitor connections** in production
5. **Consider WebSockets** if you need bidirectional communication

## Support

If you encounter issues:
1. Check the browser's Network tab for SSE connection status
2. Use the test endpoints to verify connectivity
3. Check Django logs for authentication errors
4. Use the Python test client for debugging

The implementation is production-ready and handles all the common SSE pitfalls with Django REST Framework!
