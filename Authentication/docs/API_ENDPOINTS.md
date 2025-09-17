# Authentication API Endpoints

## Overview

This document provides detailed information about all authentication-related API endpoints, including the new SSE (Server-Sent Events) functionality for real-time notifications.

## Base URL

```
http://localhost:8000/api/v1/auth/
```

## Authentication

All protected endpoints require a valid JWT access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### 1. User Registration

**POST** `/register/`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid data or user already exists
- `422 Unprocessable Entity`: Validation errors

### 2. User Login (Single Device)

**POST** `/login/`

Authenticate user and obtain JWT tokens. This endpoint enforces single-device login.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Behavior:**
- If user is already logged in on another device, the previous access token becomes invalid
- SSE notifications are sent to existing sessions with `FORCE_LOGOUT` event
- Only the latest login session remains active

**Error Responses:**
- `400 Bad Request`: Invalid credentials
- `401 Unauthorized`: Authentication failed

### 3. Token Refresh

**POST** `/refresh/`

Refresh an access token using a valid refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Behavior:**
- Updates the user's `current_jti` with the new access token's JTI
- Sends SSE notifications to other sessions if JTI changes
- Only the refresh token from the latest login remains valid

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token

### 4. User Profile

**GET** `/user/`

Retrieve the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "current_jti": "abc123def456"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired access token
- `401 Unauthorized`: Token from old device (single-device enforcement)

### 5. All Users (Admin Only)

**GET** `/users/all/`

Retrieve a list of all users (admin access required).

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "email": "user1@example.com",
    "username": "user1",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student"
  },
  {
    "id": 2,
    "email": "admin@example.com",
    "username": "admin",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin"
  }
]
```

**Error Responses:**
- `401 Unauthorized`: Invalid access token
- `403 Forbidden`: Insufficient permissions

### 6. SSE Notifications (Real-time)

**GET** `/sse/notifications/`

Establish a Server-Sent Events connection for real-time notifications.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no

event: heartbeat
data: {}

event: message
data: {"type":"FORCE_LOGOUT","data":{"message":"Your account was logged in from another device."}}
```

**Event Types:**

1. **Heartbeat Events** (every 30 seconds):
   ```
   event: heartbeat
   data: {}
   ```

2. **Force Logout Events**:
   ```
   event: message
   data: {"type":"FORCE_LOGOUT","data":{"message":"Your account was logged in from another device."}}
   ```

**Client Implementation Example:**
```javascript
const eventSource = new EventSource('/api/v1/auth/sse/notifications/', {
  headers: {
    'Authorization': 'Bearer ' + accessToken
  }
});

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'FORCE_LOGOUT') {
    alert(data.data.message);
    // Handle logout
    window.location.href = '/login';
  }
};

eventSource.onerror = function(error) {
  console.error('SSE error:', error);
  // Handle reconnection
};
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired access token
- `403 Forbidden`: Authentication required

## Error Handling

### Standard Error Response Format

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "details": {
    "field_name": ["Field specific error messages"]
  }
}
```

### Common Error Codes

- `invalid_credentials`: Wrong email/password combination
- `token_expired`: JWT token has expired
- `token_invalid`: JWT token is malformed or invalid
- `device_changed`: Token is from a different device (single-device enforcement)
- `permission_denied`: Insufficient permissions for the requested action
- `validation_error`: Request data validation failed

## Rate Limiting

Rate limiting is applied to prevent abuse:

- **Login attempts**: 5 attempts per minute per IP
- **Registration**: 3 attempts per minute per IP
- **SSE connections**: 5 concurrent connections per user
- **Token refresh**: 10 attempts per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1634567890
```

## Security Headers

All responses include security headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## CORS Configuration

For cross-origin requests, the following CORS headers are supported:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400
```

## WebSocket Alternative

For environments where SSE is not suitable, a WebSocket endpoint is available:

**WebSocket** `ws://localhost:8000/ws/notifications/`

**Connection Parameters:**
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/notifications/?token=' + accessToken);
```

**Message Format:**
```json
{
  "type": "FORCE_LOGOUT",
  "data": {
    "message": "Your account was logged in from another device."
  }
}
```

## Testing with cURL

### Login Request
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Authenticated Request
```bash
curl -X GET http://localhost:8000/api/v1/auth/user/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### SSE Connection
```bash
curl -N -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  http://localhost:8000/api/v1/auth/sse/notifications/
```

## Postman Collection

A Postman collection is available at:
`/Authentication/tests/authentication_tests.postman_collection.json`

Import this collection to quickly test all endpoints with pre-configured requests.

## Status Codes Summary

| Code | Description | Usage |
|------|-------------|-------|
| 200  | OK | Successful GET, PUT requests |
| 201  | Created | Successful POST requests (registration) |
| 400  | Bad Request | Invalid request data |
| 401  | Unauthorized | Authentication required/failed |
| 403  | Forbidden | Insufficient permissions |
| 404  | Not Found | Resource not found |
| 422  | Unprocessable Entity | Validation errors |
| 429  | Too Many Requests | Rate limit exceeded |
| 500  | Internal Server Error | Server error |
