# API Authentication

## Authentication Methods

### 1. API Keys

Simple, suitable for server-to-server communication.

**Header-based (Recommended)**
```
X-API-Key: your-api-key-here
```

**Query parameter (Less secure)**
```
GET /users?api_key=your-api-key-here
```

**Implementation Considerations:**
- Generate cryptographically secure keys (32+ characters)
- Store hashed in database
- Allow key rotation
- Set expiration dates
- Track usage per key

### 2. JWT (JSON Web Tokens)

Stateless authentication for user sessions.

**Structure:** `header.payload.signature`

**Header**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload**
```json
{
  "sub": "user-123",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "admin",
  "iat": 1699900000,
  "exp": 1699986400
}
```

**Usage**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Best Practices:**
- Short expiration (15-60 minutes)
- Use refresh tokens for renewal
- Include minimal claims
- Sign with strong secret (HS256) or keys (RS256)
- Validate all claims on server

### 3. OAuth 2.0

For third-party access and delegated authorization.

**Grant Types:**

**Authorization Code (Web apps)**
```
1. Redirect to: /authorize?response_type=code&client_id=xxx&redirect_uri=xxx&scope=read
2. User authenticates
3. Redirect back with: ?code=abc123
4. Exchange code for token: POST /token {code, client_id, client_secret}
5. Receive: {access_token, refresh_token, expires_in}
```

**Client Credentials (Server-to-server)**
```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=xxx&client_secret=xxx&scope=read
```

**Refresh Token**
```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&refresh_token=xxx&client_id=xxx
```

### 4. Session-based

Traditional cookie-based sessions.

```
Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Strict
```

**When to use:**
- Browser-based apps
- When state storage is acceptable
- CSRF protection required

## Token Lifecycle

### Access Token
- Short-lived (15-60 minutes)
- Used for API requests
- Stored in memory (not localStorage)

### Refresh Token
- Long-lived (days/weeks)
- Used only to get new access tokens
- Stored securely (httpOnly cookie)
- Revocable

### Token Refresh Flow
```
1. Access token expires
2. Client sends refresh token to /token
3. Server validates refresh token
4. Server issues new access + refresh tokens
5. Old refresh token invalidated (rotation)
```

## Authorization Patterns

### Role-Based Access Control (RBAC)
```json
{
  "user_id": 123,
  "roles": ["admin", "editor"],
  "permissions": ["users:read", "users:write", "posts:*"]
}
```

### Scope-Based (OAuth)
```
scope=read:users write:posts
```

### Resource-Based
```python
def can_edit(user, resource):
    return user.id == resource.owner_id or user.has_role("admin")
```

## Security Headers

### Request
```
Authorization: Bearer <token>
X-API-Key: <key>
```

### Response
```
WWW-Authenticate: Bearer realm="api"
```

## Common Endpoints

```
POST /auth/register     # Create account
POST /auth/login        # Get tokens
POST /auth/logout       # Invalidate tokens
POST /auth/refresh      # Refresh access token
POST /auth/forgot       # Request password reset
POST /auth/reset        # Reset password
GET  /auth/me           # Get current user
```

## Error Responses

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "error": "forbidden",
  "message": "Insufficient permissions for this action"
}
```
