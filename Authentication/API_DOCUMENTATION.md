# Authentication API Documentation

## Overview

This API provides endpoints for user authentication with single-device enforcement. It uses JWT (JSON Web Tokens) for authentication and ensures that users can only be logged in from one device at a time.

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

### Register User

Create a new user account.

```http
POST /register/
```

#### Request Body

| Field    | Type   | Required | Description                |
|----------|--------|----------|----------------------------|
| email    | string | Yes      | User's email address      |
| username | string | Yes      | User's username           |
| password | string | Yes      | User's password           |

#### Example Request
```json
{
    "email": "user@example.com",
    "username": "username",
    "password": "password123"
}
```

#### Example Response
```json
{
    "message": "User registered successfully."
}
```

Status: 201 Created

### Login

Authenticate user and receive access and refresh tokens.

```http
POST /login/
```

#### Request Body

| Field    | Type   | Required | Description           |
|----------|--------|----------|-----------------------|
| email    | string | Yes      | User's email address |
| password | string | Yes      | User's password      |

#### Example Request
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

#### Example Response
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Status: 200 OK

### Refresh Token

Get a new access token using a refresh token.

```http
POST /refresh/
```

#### Request Body

| Field   | Type   | Required | Description    |
|---------|--------|----------|----------------|
| refresh | string | Yes      | Refresh token |

#### Example Request
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Example Response
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Status: 200 OK

### Get User Profile

Get the current user's profile information.

```http
GET /user/
```

#### Headers
```
Authorization: Bearer <access_token>
```

#### Example Response
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "role": "user"
}
```

Status: 200 OK

### List All Users

Get a list of all users (admin only).

```http
GET /users/all/
```

#### Headers
```
Authorization: Bearer <access_token>
```

#### Example Response
```json
[
    {
        "id": 1,
        "email": "user@example.com",
        "username": "username",
        "role": "user"
    },
    {
        "id": 2,
        "email": "admin@example.com",
        "username": "admin",
        "role": "admin"
    }
]
```

Status: 200 OK

## Error Responses

### Invalid Credentials
```json
{
    "message": "Invalid email or password"
}
```
Status: 400 Bad Request

### Token Invalid
```json
{
    "detail": "Token is no longer valid. Please log in again."
}
```
Status: 401 Unauthorized

### Token Expired
```json
{
    "detail": "Token has expired"
}
```
Status: 401 Unauthorized

### Invalid Token Format
```json
{
    "detail": "Invalid token header. No credentials provided."
}
```
Status: 401 Unauthorized

### Permission Denied
```json
{
    "detail": "You do not have permission to perform this action."
}
```
Status: 403 Forbidden

## Single-Device Enforcement

The API enforces a single-device policy:

1. When a user logs in from a new device, any existing access tokens from other devices become invalid.
2. The refresh token from the previous device remains valid and can be used to obtain new access tokens.
3. Each access token contains a unique JTI (JWT ID) that is stored in the user's profile.
4. Only requests with access tokens matching the stored JTI are allowed.

## Rate Limiting

- Login attempts are limited to 5 per minute per IP address
- Token refresh attempts are limited to 10 per minute per user
- API endpoints are limited to 100 requests per minute per user

## Security Recommendations

1. Always use HTTPS in production
2. Store tokens securely on the client side
3. Implement token refresh before access token expiration
4. Handle token invalidation gracefully in your frontend application
5. Implement proper error handling for authentication failures

## Testing

The API includes comprehensive test coverage. You can run the tests using:

```bash
python manage.py test Authentication.tests.test_authentication
```

The tests cover:
- User registration
- Login functionality
- Token refresh
- Single-device enforcement
- Multi-device scenarios
- Error cases
