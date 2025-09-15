# Single-Device Authentication System

This module implements a secure single-device authentication system using Django REST Framework and Simple JWT. The system ensures that users can only be actively logged in from one device at a time, enhancing security and preventing unauthorized concurrent access.

## Features

- Single-device enforcement: Only one active device session per user
- Automatic invalidation of old sessions when logging in from a new device
- JWT-based authentication with access and refresh tokens
- Secure token refresh mechanism
- Comprehensive test coverage

## Technical Implementation

### Models

The authentication system extends Django's built-in User model with additional fields:

```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    current_jti = models.CharField(max_length=255, blank=True, null=True)  # Stores current valid JWT ID
    role = models.CharField(max_length=20, choices=ROLES, default="user")
```

### Authentication Flow

1. **User Login**
   - User provides email and password
   - System generates new access and refresh tokens
   - New token's JTI (JWT ID) is stored in user's current_jti field
   - Previous access tokens become invalid

2. **Token Validation**
   - Each request's access token JTI is compared with user's current_jti
   - Requests with non-matching JTIs are rejected
   - Only the latest device's access token is valid

3. **Token Refresh**
   - Refresh tokens remain valid even after new device login
   - New access tokens inherit the latest JTI
   - Old access tokens are automatically invalidated

## API Endpoints

### 1. User Registration
```http
POST /api/v1/auth/register/
```
Request body:
```json
{
    "email": "user@example.com",
    "username": "username",
    "password": "password123"
}
```

### 2. User Login
```http
POST /api/v1/auth/login/
```
Request body:
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```
Response:
```json
{
    "refresh": "refresh_token_string",
    "access": "access_token_string"
}
```

### 3. Token Refresh
```http
POST /api/v1/auth/refresh/
```
Request body:
```json
{
    "refresh": "refresh_token_string"
}
```
Response:
```json
{
    "access": "new_access_token_string"
}
```

### 4. User Profile
```http
GET /api/v1/auth/user/
```
Headers:
```
Authorization: Bearer access_token_string
```

### 5. List All Users (Admin only)
```http
GET /api/v1/auth/users/all/
```
Headers:
```
Authorization: Bearer access_token_string
```

## Error Responses

### Authentication Failed
```json
{
    "detail": "Token is no longer valid. Please log in again."
}
```
Status Code: 401

### Invalid Credentials
```json
{
    "message": "Invalid email or password"
}
```
Status Code: 400

## Testing

The system includes comprehensive test coverage for all authentication scenarios:

1. Single device login and token validation
2. Multi-device login behavior
3. Token refresh functionality
4. Access token invalidation
5. Concurrent refresh token handling

Run tests using:
```bash
python manage.py test Authentication.tests.test_authentication
```

## Security Considerations

1. **Token Storage**
   - Store tokens securely on the client side
   - Never store access tokens in localStorage
   - Use secure HTTP-only cookies when possible

2. **Token Lifetimes**
   - Access tokens: 1 day
   - Refresh tokens: 7 days

3. **Device Management**
   - Only the latest logged-in device maintains active access
   - Previous sessions are automatically invalidated
   - Refresh tokens from old sessions may still work (configurable)

## Integration Guide

1. **Setup Authentication Headers**
```javascript
const headers = {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
};
```

2. **Handle Token Refresh**
```javascript
async function refreshToken(refreshToken) {
    const response = await fetch('/api/v1/auth/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
    });
    return response.json();
}
```

3. **Handle Token Invalidation**
```javascript
function handleTokenInvalidation(error) {
    if (error.status === 401) {
        // Redirect to login page or refresh token
        redirectToLogin();
    }
}
```

## Dependencies

- Django REST Framework
- Simple JWT
- Django

## Configuration

Key settings in `settings.py`:
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
}
```
