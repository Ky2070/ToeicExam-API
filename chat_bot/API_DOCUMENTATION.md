# Chat Bot API Documentation

This document describes the REST API endpoints for the Chat Bot application with a 3-layer architecture (Controllers, Services, Repositories) and user authentication.

## Architecture Overview

The Chat Bot API follows a clean 3-layer architecture:

1. **Controllers** (`controllers/`): Handle HTTP requests/responses and API validation
2. **Services** (`services/`): Contain business logic and coordinate between layers
3. **Repositories** (`repositories/`): Handle direct database operations

## Authentication

All API endpoints require authentication. Users can only access their own messages. Any attempt to access messages from other users will return HTTP 403 Forbidden.

## Models

### User
Uses the existing `Authentication.models.User` model with the following fields:
- `id`: Primary key
- `username`: User's username
- `email`: User's email (unique)
- `password`: Hashed password
- `role`: User role (admin, user, teacher, student)
- `is_active`: Whether user is active
- `date_joined`: When user was created

### Message
- `id`: Primary key
- `user`: Foreign key to User
- `role`: Message role (user, bot, system)
- `content`: Message content
- `created_at`: When message was created

## API Endpoints

Base URL: `/api/v1/chat-bot/`

**Authentication Required**: All endpoints require a valid authentication token.

### Message Endpoints

#### GET /messages/
Get all messages for the authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "user": 1,
            "user_username": "john_doe",
            "role": "user",
            "content": "Hello, how are you?",
            "created_at": "2024-01-01T12:00:00Z"
        },
        {
            "id": 2,
            "user": 1,
            "user_username": "john_doe",
            "role": "bot",
            "content": "Hi! I'm doing well, thank you for asking!",
            "created_at": "2024-01-01T12:01:00Z"
        }
    ],
    "count": 2
}
```

#### POST /messages/
Create a new message for the authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
    "role": "user",
    "content": "What's the weather like today?"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 3,
        "user": 1,
        "user_username": "john_doe",
        "role": "user",
        "content": "What's the weather like today?",
        "created_at": "2024-01-01T12:02:00Z"
    },
    "message": "Message created successfully"
}
```

#### GET /messages/{id}/
Get message by ID (only if it belongs to the authenticated user).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "user": 1,
        "user_username": "john_doe",
        "role": "user",
        "content": "Hello, how are you?",
        "created_at": "2024-01-01T12:00:00Z"
    }
}
```

**Error Response (if message doesn't belong to user):**
```json
{
    "success": false,
    "errors": ["Message not found or access denied"]
}
```
Status: `403 Forbidden`

#### PUT /messages/{id}/
Update message by ID (only if it belongs to the authenticated user).

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
    "content": "Hello, how are you doing today?"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "user": 1,
        "user_username": "john_doe",
        "role": "user",
        "content": "Hello, how are you doing today?",
        "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "Message updated successfully"
}
```

#### DELETE /messages/{id}/
Delete message by ID (only if it belongs to the authenticated user).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Message deleted successfully"
}
```

### Utility Endpoints

#### GET /messages/history/
Get conversation history for the authenticated user (with optional limit).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (optional): Number of recent messages to return

**Examples:**
- `/messages/history/` - Get all messages
- `/messages/history/?limit=10` - Get last 10 messages

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "user": 1,
            "user_username": "john_doe",
            "role": "user",
            "content": "Hello",
            "created_at": "2024-01-01T12:00:00Z"
        },
        {
            "id": 2,
            "user": 1,
            "user_username": "john_doe",
            "role": "bot",
            "content": "Hi there!",
            "created_at": "2024-01-01T12:01:00Z"
        }
    ],
    "count": 2
}
```

#### DELETE /messages/clear/
Delete all messages for the authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Deleted 5 messages successfully"
}
```

#### GET /messages/by-role/
Get messages filtered by role for the authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `role` (required): Message role to filter by (user, bot, system)

**Example:**
- `/messages/by-role/?role=user` - Get all user messages

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "user": 1,
            "user_username": "john_doe",
            "role": "user",
            "content": "Hello",
            "created_at": "2024-01-01T12:00:00Z"
        }
    ],
    "count": 1
}
```

#### GET /messages/count/
Get total message count for the authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "count": 15
}
```

## Error Responses

### Authentication Errors

**401 Unauthorized:**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### Permission Errors

**403 Forbidden:**
```json
{
    "success": false,
    "errors": ["Message not found or access denied"]
}
```

### Validation Errors

**400 Bad Request:**
```json
{
    "success": false,
    "errors": {
        "role": ["Role must be one of: user, bot, system"],
        "content": ["This field may not be blank."]
    }
}
```

### Server Errors

**500 Internal Server Error:**
```json
{
    "success": false,
    "error": "Internal server error message"
}
```

## HTTP Status Codes

- `200 OK`: Successful GET, PUT, DELETE operations
- `201 Created`: Successful POST operations
- `400 Bad Request`: Validation errors or bad input
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied (trying to access other user's messages)
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server errors

## Message Roles

Valid message roles:
- `user`: Messages from the user
- `bot`: Messages from the chatbot
- `system`: System messages

## Authentication

This API uses the existing authentication system. Users must be authenticated to access any endpoints. The authentication provides:

1. **User Identification**: `request.user.id` is used to identify the current user
2. **Message Ownership**: Users can only access their own messages
3. **Automatic Association**: New messages are automatically linked to the authenticated user

## Usage Examples

### Creating a Chat Session

1. Authenticate user (using existing auth system):
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

2. Send a user message:
```bash
curl -X POST http://localhost:8000/api/v1/chat-bot/messages/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"role": "user", "content": "Hello, I need help with my account"}'
```

3. Send a bot response:
```bash
curl -X POST http://localhost:8000/api/v1/chat-bot/messages/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"role": "bot", "content": "Hi! I would be happy to help you with your account. What specific issue are you experiencing?"}'
```

4. Get conversation history:
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/chat-bot/messages/history/
```

### Updating a Message

```bash
curl -X PUT http://localhost:8000/api/v1/chat-bot/messages/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"content": "Updated message content"}'
```

### Getting Messages by Role

```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/chat-bot/messages/by-role/?role=user"
```

## Security Features

1. **Authentication Required**: All endpoints require valid authentication
2. **User Isolation**: Users can only access their own messages
3. **Permission Checks**: All operations verify message ownership
4. **Input Validation**: All inputs are validated before processing
5. **Error Handling**: Consistent error responses without sensitive information

## Testing

Run the test suite:
```bash
python manage.py test chat_bot
```

The test suite includes:
- Authentication and permission tests
- Message CRUD operations
- Conversation history
- Error handling
- Model validation
- Security tests (access control)

## Changes from Previous Version

1. **Removed User CRUD**: No longer includes user management endpoints
2. **Authentication Required**: All endpoints now require authentication
3. **User Isolation**: Users can only access their own messages
4. **Simplified URLs**: Removed user ID from URLs (uses authenticated user automatically)
5. **Permission Checks**: Added proper ownership validation for all operations
6. **Security Enhanced**: Prevents cross-user data access