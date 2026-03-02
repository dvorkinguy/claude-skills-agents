# API Error Handling

## RFC 7807 Problem Details

Standard format for HTTP API errors.

### Structure
```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request body contains invalid data",
  "instance": "/users/123"
}
```

### Fields
| Field | Required | Description |
|-------|----------|-------------|
| type | Yes | URI identifying error type |
| title | Yes | Short, human-readable summary |
| status | Yes | HTTP status code |
| detail | No | Detailed explanation |
| instance | No | URI of specific occurrence |

### Extended Fields
Add custom fields as needed:
```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "Multiple validation errors occurred",
  "errors": [
    {
      "field": "email",
      "code": "invalid_format",
      "message": "Email format is invalid"
    },
    {
      "field": "age",
      "code": "out_of_range",
      "message": "Age must be between 0 and 150"
    }
  ],
  "request_id": "req-abc123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Types

### Validation Errors (422)
```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "code": "invalid_format"
    }
  ]
}
```

### Authentication Error (401)
```json
{
  "type": "https://api.example.com/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Invalid or expired access token"
}
```

### Authorization Error (403)
```json
{
  "type": "https://api.example.com/errors/forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "You don't have permission to access this resource"
}
```

### Not Found (404)
```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "User with ID 999 not found"
}
```

### Conflict (409)
```json
{
  "type": "https://api.example.com/errors/conflict",
  "title": "Conflict",
  "status": 409,
  "detail": "Email address already registered"
}
```

### Rate Limit (429)
```json
{
  "type": "https://api.example.com/errors/rate-limit",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded",
  "retry_after": 60
}
```

### Internal Error (500)
```json
{
  "type": "https://api.example.com/errors/internal",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred",
  "request_id": "req-abc123"
}
```

## Error Codes

Define consistent error codes:
```
# Authentication
auth/invalid_token
auth/expired_token
auth/missing_token

# Validation
validation/required_field
validation/invalid_format
validation/out_of_range
validation/invalid_type

# Resource
resource/not_found
resource/already_exists
resource/conflict

# Rate Limiting
rate_limit/exceeded
rate_limit/quota_exceeded

# Server
server/internal_error
server/service_unavailable
server/timeout
```

## Implementation Patterns

### Exception Classes
```python
class APIError(Exception):
    def __init__(self, status: int, type: str, title: str, detail: str = None):
        self.status = status
        self.type = type
        self.title = title
        self.detail = detail

class ValidationError(APIError):
    def __init__(self, errors: list):
        super().__init__(
            status=422,
            type="https://api.example.com/errors/validation",
            title="Validation Error",
            detail="Request validation failed"
        )
        self.errors = errors

class NotFoundError(APIError):
    def __init__(self, resource: str, id: any):
        super().__init__(
            status=404,
            type="https://api.example.com/errors/not-found",
            title="Not Found",
            detail=f"{resource} with ID {id} not found"
        )
```

### Global Exception Handler
```python
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    response = {
        "type": exc.type,
        "title": exc.title,
        "status": exc.status,
        "detail": exc.detail,
        "instance": str(request.url.path)
    }

    if hasattr(exc, 'errors'):
        response["errors"] = exc.errors

    return JSONResponse(
        status_code=exc.status,
        content=response,
        headers={"Content-Type": "application/problem+json"}
    )
```

## Development vs Production

### Development
Include detailed information:
```json
{
  "type": "https://api.example.com/errors/internal",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "Division by zero in calculate_total()",
  "stack_trace": "Traceback (most recent call last):\n  File...",
  "request_id": "req-abc123"
}
```

### Production
Hide sensitive details:
```json
{
  "type": "https://api.example.com/errors/internal",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred",
  "request_id": "req-abc123"
}
```

## Content-Type

Use `application/problem+json`:
```
Content-Type: application/problem+json
```

## Client Handling

```javascript
async function apiRequest(url, options) {
  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.json();

    switch (error.status) {
      case 401:
        // Redirect to login
        break;
      case 422:
        // Show validation errors
        displayErrors(error.errors);
        break;
      case 429:
        // Retry after delay
        await sleep(error.retry_after * 1000);
        return apiRequest(url, options);
      default:
        // Show generic error
        showError(error.title);
    }

    throw new APIError(error);
  }

  return response.json();
}
```
