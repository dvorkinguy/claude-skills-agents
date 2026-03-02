---
name: rest-api-architect
description: Build REST APIs with best practices. Use when creating APIs, designing endpoints, implementing authentication (JWT, OAuth, API keys), adding rate limiting, setting up CORS, documenting with OpenAPI/Swagger, handling errors, or implementing pagination. Covers FastAPI, Flask, Express patterns.
---

# REST API Architect

Build production-ready REST APIs with industry best practices.

## Quick Reference

### HTTP Methods
| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Retrieve resource | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Replace resource | Yes | No |
| PATCH | Partial update | No | No |
| DELETE | Remove resource | Yes | No |

### Status Codes Cheat Sheet
```
Success:     200 OK, 201 Created, 204 No Content
Redirect:    301 Moved, 304 Not Modified
Client Err:  400 Bad Request, 401 Unauthorized, 403 Forbidden
             404 Not Found, 409 Conflict, 422 Unprocessable, 429 Too Many
Server Err:  500 Internal, 502 Bad Gateway, 503 Unavailable
```

### URL Design
```
GET    /users              # List users
POST   /users              # Create user
GET    /users/{id}         # Get user
PUT    /users/{id}         # Replace user
PATCH  /users/{id}         # Update user
DELETE /users/{id}         # Delete user
GET    /users/{id}/orders  # User's orders
```

### Query Parameters
```
?page=1&limit=20           # Pagination
?sort=created_at:desc      # Sorting
?status=active&type=admin  # Filtering
?fields=id,name,email      # Field selection
```

### Authentication Header
```
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
```

### Error Response (RFC 7807)
```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "Email format is invalid",
  "instance": "/users",
  "errors": [{"field": "email", "message": "Invalid format"}]
}
```

### Pagination Response
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "pages": 8,
  "next": "/users?page=2&limit=20",
  "prev": null
}
```

### Cache Headers
```
Cache-Control: max-age=3600, public
ETag: "abc123"
Last-Modified: Wed, 15 Nov 2023 12:45:26 GMT
```

## Reference Documents

### Design
- `references/design-fundamentals.md` - REST principles, resource naming
- `references/status-codes.md` - Complete HTTP status code reference
- `references/pagination-filtering.md` - Pagination and filtering patterns
- `references/caching.md` - Cache headers and strategies

### Security
- `references/authentication.md` - JWT, OAuth2, API keys
- `references/security.md` - Rate limiting, CORS, OWASP

### Documentation
- `references/documentation.md` - OpenAPI/Swagger, versioning
- `references/error-handling.md` - Error formats, RFC 7807

### Implementations
- `references/implementations/python-fastapi.md` - FastAPI patterns
- `references/implementations/python-flask.md` - Flask patterns
- `references/implementations/nodejs-express.md` - Express patterns
- `references/implementations/database-patterns.md` - ORM, repository pattern
