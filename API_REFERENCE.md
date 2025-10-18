# Autogram API Reference

Complete reference for all API endpoints with examples.

## Base URLs

- **Development**: http://localhost:8000
- **Production**: https://your-domain.com

All API endpoints are prefixed with `/api`

## Authentication

Admin endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

Get a token by logging in via `/api/admin/login`

---

## Public Endpoints

These endpoints do not require authentication.

### 1. Get Notices

Get announcement information including KakaoTalk link, QR code, and notices.

**Endpoint**: `GET /api/notices`

**Authentication**: None

**Response**: 200 OK

```json
{
  "kakao_talk_link": "https://open.kakao.com/o/xxxxx",
  "qr_code_url": "https://example.com/qr.png",
  "notices": [
    {
      "id": 1,
      "title": "Welcome to Autogram",
      "content": "Start exchanging Instagram comments today!",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Example**:

```bash
curl -X GET "http://localhost:8000/api/notices"
```

---

### 2. Get Requests By Week

Get weekly Instagram post submissions, with optional filtering.

**Endpoint**: `GET /api/requests-by-week`

**Authentication**: None

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | string | No | Filter by username |
| week_number | integer | No | ISO week number (1-53) |
| year | integer | No | Year (e.g., 2024) |
| skip | integer | No | Pagination offset (default: 0) |
| limit | integer | No | Page size (default: 100, max: 500) |

**Response**: 200 OK

```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "username": "user1",
      "week_number": 42,
      "year": 2024,
      "instagram_link": "https://www.instagram.com/p/ABC123/",
      "created_at": "2024-10-15T10:30:00Z"
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 100
}
```

**Examples**:

```bash
# Get all requests
curl -X GET "http://localhost:8000/api/requests-by-week"

# Filter by username
curl -X GET "http://localhost:8000/api/requests-by-week?username=user1"

# Filter by week and year
curl -X GET "http://localhost:8000/api/requests-by-week?week_number=42&year=2024"

# Pagination
curl -X GET "http://localhost:8000/api/requests-by-week?skip=10&limit=20"
```

---

### 3. Get User Action Verification

Get verification data showing who hasn't commented on which links.

**Endpoint**: `GET /api/user-action-verification`

**Authentication**: None

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | string | No | Filter by username |
| is_verified | boolean | No | Filter by verification status |
| skip | integer | No | Pagination offset (default: 0) |
| limit | integer | No | Page size (default: 100, max: 500) |

**Response**: 200 OK

```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "username": "user1",
      "request_id": 5,
      "instagram_link": "https://www.instagram.com/p/ABC123/",
      "is_verified": false,
      "verified_at": null,
      "created_at": "2024-10-15T10:30:00Z"
    }
  ],
  "total": 25,
  "skip": 0,
  "limit": 100
}
```

**Examples**:

```bash
# Get all verifications
curl -X GET "http://localhost:8000/api/user-action-verification"

# Get unverified actions
curl -X GET "http://localhost:8000/api/user-action-verification?is_verified=false"

# Filter by username
curl -X GET "http://localhost:8000/api/user-action-verification?username=user1"
```

---

### 4. Register Consumer

Register an Instagram account to receive AI auto-comments on posts.

**Endpoint**: `POST /api/consumer`

**Authentication**: None

**Request Body**:

```json
{
  "instagram_id": "your_instagram_username"
}
```

**Response**: 201 Created

```json
{
  "id": 1,
  "instagram_id": "your_instagram_username",
  "is_active": true,
  "created_at": "2024-10-18T10:00:00Z",
  "updated_at": null
}
```

**Errors**:

- **409 Conflict**: Instagram ID already registered
- **400 Bad Request**: Invalid instagram_id

**Example**:

```bash
curl -X POST "http://localhost:8000/api/consumer" \
  -H "Content-Type: application/json" \
  -d '{
    "instagram_id": "myusername"
  }'
```

---

### 5. Register Producer

Register an Instagram account to provide AI auto-commenting service.

**Endpoint**: `POST /api/producer`

**Authentication**: None

**Request Body**:

```json
{
  "instagram_id": "your_instagram_username",
  "password": "your_instagram_password",
  "verification_code": "CODE123"
}
```

**Response**: 201 Created

```json
{
  "id": 1,
  "instagram_id": "your_instagram_username",
  "is_verified": true,
  "is_active": true,
  "created_at": "2024-10-18T10:00:00Z",
  "updated_at": null
}
```

**Errors**:

- **409 Conflict**: Instagram ID already registered
- **400 Bad Request**: Invalid credentials or verification code
- **503 Service Unavailable**: Instagram login failed

**Example**:

```bash
curl -X POST "http://localhost:8000/api/producer" \
  -H "Content-Type: application/json" \
  -d '{
    "instagram_id": "myusername",
    "password": "mypassword",
    "verification_code": "ABC123"
  }'
```

**Security Notes**:
- Password is encrypted before storage
- Verification code validates ownership
- Session is saved for future use

---

### 6. Check Unfollowers

Check who unfollowed you on Instagram.

**Endpoint**: `POST /api/unfollow-checker`

**Authentication**: None

**Request Body**:

```json
{
  "instagram_id": "your_instagram_username",
  "password": "your_instagram_password",
  "verification_code": "CODE123"
}
```

**Response**: 200 OK

```json
{
  "instagram_id": "your_instagram_username",
  "followers_count": 1500,
  "following_count": 800,
  "unfollowers_count": 150,
  "unfollowers": [
    "user1",
    "user2",
    "user3"
  ],
  "checked_at": "2024-10-18T10:00:00Z"
}
```

**Errors**:

- **400 Bad Request**: Invalid credentials or verification code
- **503 Service Unavailable**: Instagram API error or rate limited

**Example**:

```bash
curl -X POST "http://localhost:8000/api/unfollow-checker" \
  -H "Content-Type: application/json" \
  -d '{
    "instagram_id": "myusername",
    "password": "mypassword",
    "verification_code": "ABC123"
  }'
```

**Rate Limiting**: This endpoint is resource-intensive. Use sparingly.

---

## Admin Endpoints

These endpoints require JWT authentication.

### Authentication Flow

#### 1. Admin Login

Get a JWT access token.

**Endpoint**: `POST /api/admin/login`

**Authentication**: None (this is the login endpoint)

**Request Body** (form-encoded):

```
username=admin
password=your_password
```

**Response**: 200 OK

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors**:

- **401 Unauthorized**: Invalid credentials or inactive account

**Example**:

```bash
curl -X POST "http://localhost:8000/api/admin/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Using the token**:

```bash
# Save token
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Use in requests
curl -X GET "http://localhost:8000/api/admin/me" \
  -H "Authorization: Bearer $TOKEN"
```

---

#### 2. Get Current Admin

Get information about the currently authenticated admin.

**Endpoint**: `GET /api/admin/me`

**Authentication**: Required (JWT)

**Response**: 200 OK

```json
{
  "id": 1,
  "username": "admin",
  "is_active": true,
  "last_login_at": "2024-10-18T10:00:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Errors**:

- **401 Unauthorized**: Invalid or expired token

**Example**:

```bash
curl -X GET "http://localhost:8000/api/admin/me" \
  -H "Authorization: Bearer $TOKEN"
```

---

### SNS Users Management

#### 3. List SNS Users

Get a list of all SNS raise users.

**Endpoint**: `GET /api/admin/sns-users`

**Authentication**: Required (JWT)

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| skip | integer | No | Pagination offset (default: 0) |
| limit | integer | No | Page size (default: 100, max: 500) |

**Response**: 200 OK

```json
{
  "items": [
    {
      "id": 1,
      "username": "user1",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": null
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 100
}
```

**Example**:

```bash
curl -X GET "http://localhost:8000/api/admin/sns-users" \
  -H "Authorization: Bearer $TOKEN"
```

---

#### 4. Create SNS User

Create a new SNS raise user.

**Endpoint**: `POST /api/admin/sns-users`

**Authentication**: Required (JWT)

**Request Body**:

```json
{
  "username": "newuser"
}
```

**Response**: 201 Created

```json
{
  "id": 51,
  "username": "newuser",
  "created_at": "2024-10-18T10:00:00Z",
  "updated_at": null
}
```

**Errors**:

- **409 Conflict**: Username already exists
- **400 Bad Request**: Invalid username

**Example**:

```bash
curl -X POST "http://localhost:8000/api/admin/sns-users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser"
  }'
```

---

#### 5. Update SNS User

Update an existing SNS raise user.

**Endpoint**: `PUT /api/admin/sns-users/{id}`

**Authentication**: Required (JWT)

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| id | integer | User ID |

**Request Body**:

```json
{
  "username": "updatedusername"
}
```

**Response**: 200 OK

```json
{
  "id": 51,
  "username": "updatedusername",
  "created_at": "2024-10-18T10:00:00Z",
  "updated_at": "2024-10-18T11:00:00Z"
}
```

**Errors**:

- **404 Not Found**: User ID not found
- **409 Conflict**: Username already exists

**Example**:

```bash
curl -X PUT "http://localhost:8000/api/admin/sns-users/51" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "updatedusername"
  }'
```

---

#### 6. Delete SNS User

Delete an SNS raise user and all related data (cascade delete).

**Endpoint**: `DELETE /api/admin/sns-users/{id}`

**Authentication**: Required (JWT)

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| id | integer | User ID |

**Response**: 204 No Content

**Errors**:

- **404 Not Found**: User ID not found

**Example**:

```bash
curl -X DELETE "http://localhost:8000/api/admin/sns-users/51" \
  -H "Authorization: Bearer $TOKEN"
```

**Warning**: This will delete:
- The user record
- All their weekly requests
- All their action verifications

---

### Helper Accounts Management

#### 7. List Helper Accounts

Get a list of all helper Instagram accounts.

**Endpoint**: `GET /api/admin/helpers`

**Authentication**: Required (JWT)

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| skip | integer | No | Pagination offset (default: 0) |
| limit | integer | No | Page size (default: 100, max: 500) |

**Response**: 200 OK

```json
{
  "items": [
    {
      "id": 1,
      "instagram_id": "helper_account_1",
      "is_active": true,
      "last_used_at": "2024-10-18T10:00:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": null
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 100
}
```

**Example**:

```bash
curl -X GET "http://localhost:8000/api/admin/helpers" \
  -H "Authorization: Bearer $TOKEN"
```

---

#### 8. Register Helper Account

Register a new helper Instagram account with session login.

**Endpoint**: `POST /api/admin/helpers`

**Authentication**: Required (JWT)

**Request Body**:

```json
{
  "instagram_id": "helper_username",
  "password": "helper_password"
}
```

**Response**: 201 Created

```json
{
  "id": 6,
  "instagram_id": "helper_username",
  "is_active": true,
  "last_used_at": null,
  "created_at": "2024-10-18T10:00:00Z",
  "updated_at": null
}
```

**Process**:
1. Validates Instagram credentials
2. Logs in with Instaloader
3. Saves session data to database
4. Encrypts password for storage

**Errors**:

- **409 Conflict**: Instagram ID already registered
- **503 Service Unavailable**: Instagram login failed

**Example**:

```bash
curl -X POST "http://localhost:8000/api/admin/helpers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "instagram_id": "helper_account",
    "password": "securepassword"
  }'
```

**Notes**:
- Use accounts without 2FA
- Recommend using dedicated accounts, not personal ones
- Helper accounts are used for read-only operations

---

#### 9. Delete Helper Account

Delete a helper Instagram account.

**Endpoint**: `DELETE /api/admin/helpers/{id}`

**Authentication**: Required (JWT)

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| id | integer | Helper account ID |

**Response**: 204 No Content

**Errors**:

- **404 Not Found**: Helper ID not found

**Example**:

```bash
curl -X DELETE "http://localhost:8000/api/admin/helpers/6" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message or validation errors"
}
```

### Common HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET/POST request |
| 201 | Created | Successful POST creating new resource |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource (e.g., username exists) |
| 422 | Unprocessable Entity | Validation error |
| 503 | Service Unavailable | External service error (Instagram) |

### Validation Errors (422)

```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Rate Limiting

**Current Status**: Not implemented

**Recommended Limits** (for production):

| Endpoint Type | Limit | Window |
|--------------|-------|--------|
| Public endpoints | 60 requests | per minute |
| Admin login | 5 attempts | per 15 minutes |
| Instagram operations | 30 requests | per hour |

---

## Pagination

All list endpoints support pagination:

**Query Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 100, max: 500)

**Response Format**:
```json
{
  "items": [...],
  "total": 150,
  "skip": 0,
  "limit": 100
}
```

**Example**: Get page 2 with 20 items per page
```bash
curl -X GET "http://localhost:8000/api/admin/sns-users?skip=20&limit=20"
```

---

## OpenAPI Documentation

Interactive API documentation is available when the server is running:

- **Swagger UI**: http://localhost:8000/api/py/docs
- **ReDoc**: http://localhost:8000/api/py/redoc
- **OpenAPI JSON**: http://localhost:8000/api/py/openapi.json

Features:
- Try endpoints directly from the browser
- See all request/response schemas
- View validation rules
- Test authentication

---

## Code Examples

### Python (httpx)

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Login
        response = await client.post(
            "http://localhost:8000/api/admin/login",
            data={
                "username": "admin",
                "password": "admin123"
            }
        )
        token = response.json()["access_token"]

        # Use token
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(
            "http://localhost:8000/api/admin/sns-users",
            headers=headers
        )
        users = response.json()
        print(users)

asyncio.run(main())
```

### JavaScript (fetch)

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/admin/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    username: 'admin',
    password: 'admin123'
  })
});

const { access_token } = await loginResponse.json();

// Use token
const usersResponse = await fetch('http://localhost:8000/api/admin/sns-users', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

const users = await usersResponse.json();
console.log(users);
```

### cURL Scripts

```bash
#!/bin/bash

# Login and save token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/admin/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# List users
curl -X GET "http://localhost:8000/api/admin/sns-users" \
  -H "Authorization: Bearer $TOKEN" \
  | jq .

# Create user
curl -X POST "http://localhost:8000/api/admin/sns-users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser"}' \
  | jq .
```

---

## Postman Collection

### Import into Postman

1. Create a new collection "Autogram API"
2. Add environment variables:
   - `base_url`: http://localhost:8000
   - `token`: (leave empty, will be set by login)
3. Add pre-request script to login endpoint to save token

### Example Collection Structure

```
Autogram API
├── Public
│   ├── Get Notices
│   ├── Get Requests By Week
│   ├── Get User Action Verification
│   ├── Register Consumer
│   ├── Register Producer
│   └── Check Unfollowers
│
└── Admin
    ├── Auth
    │   ├── Login
    │   └── Get Current Admin
    ├── SNS Users
    │   ├── List Users
    │   ├── Create User
    │   ├── Update User
    │   └── Delete User
    └── Helpers
        ├── List Helpers
        ├── Register Helper
        └── Delete Helper
```

---

## Versioning

**Current Version**: v1 (implicit)

**Future Versioning Strategy**:
- URL-based: `/api/v1/...`, `/api/v2/...`
- Header-based: `Accept: application/vnd.autogram.v1+json`

---

## WebSocket Support

**Current Status**: Not implemented

**Planned Features** (future):
- Real-time notifications
- Live comment updates
- Progress tracking for batch operations

---

## Support

For issues with the API:
1. Check this documentation
2. View interactive docs: http://localhost:8000/api/py/docs
3. Check logs for error messages
4. Review ARCHITECTURE.md for technical details

---

**Last Updated**: 2024-10-18
**API Version**: 1.0.0
