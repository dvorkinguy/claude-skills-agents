# HTTP Status Codes Reference

## 2xx Success

### 200 OK
Request succeeded. Use for:
- GET: Resource retrieved
- PUT/PATCH: Resource updated (return updated resource)
- DELETE: Resource deleted (if returning body)

```json
// GET /users/123
{
  "id": 123,
  "name": "John Doe"
}
```

### 201 Created
Resource created successfully. Use for POST.
Include `Location` header with new resource URL.

```
POST /users
Location: /users/123

{
  "id": 123,
  "name": "John Doe"
}
```

### 204 No Content
Success with no response body. Use for:
- DELETE (preferred)
- PUT/PATCH when not returning body

```
DELETE /users/123
(empty body)
```

### 202 Accepted
Request accepted for async processing.
```json
{
  "status": "processing",
  "job_id": "abc123",
  "check_status_at": "/jobs/abc123"
}
```

## 3xx Redirection

### 301 Moved Permanently
Resource permanently moved. Client should update bookmarks.
```
Location: https://api.example.com/v2/users
```

### 302 Found
Temporary redirect.

### 304 Not Modified
Resource hasn't changed (for conditional requests with ETag/If-Modified-Since).

## 4xx Client Errors

### 400 Bad Request
Malformed request syntax, invalid JSON, etc.
```json
{
  "type": "https://api.example.com/errors/bad-request",
  "title": "Bad Request",
  "status": 400,
  "detail": "Invalid JSON: Unexpected token at position 42"
}
```

### 401 Unauthorized
Authentication required or failed.
```json
{
  "type": "https://api.example.com/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Invalid or expired access token"
}
```

### 403 Forbidden
Authenticated but not authorized for this action.
```json
{
  "type": "https://api.example.com/errors/forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "You don't have permission to delete this resource"
}
```

### 404 Not Found
Resource doesn't exist.
```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "User with ID 999 not found"
}
```

### 405 Method Not Allowed
HTTP method not supported for this endpoint.
```
Allow: GET, POST
```

### 409 Conflict
Conflict with current resource state (e.g., duplicate, version conflict).
```json
{
  "type": "https://api.example.com/errors/conflict",
  "title": "Conflict",
  "status": 409,
  "detail": "Email address already registered"
}
```

### 410 Gone
Resource permanently deleted (vs 404 which could be temporary).

### 422 Unprocessable Entity
Request understood but validation failed.
```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed",
  "errors": [
    {"field": "email", "message": "Invalid email format"},
    {"field": "age", "message": "Must be at least 18"}
  ]
}
```

### 429 Too Many Requests
Rate limit exceeded. Include retry info.
```
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1699900000

{
  "type": "https://api.example.com/errors/rate-limit",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Retry after 60 seconds"
}
```

## 5xx Server Errors

### 500 Internal Server Error
Unexpected server error. Don't expose details in production.
```json
{
  "type": "https://api.example.com/errors/internal",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred",
  "request_id": "req-abc123"  // For support/debugging
}
```

### 502 Bad Gateway
Upstream service error (when API is a proxy).

### 503 Service Unavailable
Server temporarily unavailable (maintenance, overload).
```
Retry-After: 300

{
  "type": "https://api.example.com/errors/unavailable",
  "title": "Service Unavailable",
  "status": 503,
  "detail": "Service is under maintenance. Retry in 5 minutes"
}
```

### 504 Gateway Timeout
Upstream service timeout.

## Decision Guide

### Creating Resource
```
Success → 201 Created
Duplicate → 409 Conflict
Validation fail → 422 Unprocessable Entity
```

### Getting Resource
```
Found → 200 OK
Not found → 404 Not Found
No permission → 403 Forbidden
```

### Updating Resource
```
Updated → 200 OK (with body) or 204 No Content
Not found → 404 Not Found
Validation fail → 422 Unprocessable Entity
Conflict → 409 Conflict
```

### Deleting Resource
```
Deleted → 204 No Content
Not found → 404 Not Found (or 204 for idempotency)
Cannot delete → 409 Conflict
```
