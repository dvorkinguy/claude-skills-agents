# API Security

## Rate Limiting

### Algorithms

**Token Bucket**
- Tokens added at fixed rate
- Request consumes token
- Allows bursts up to bucket size

**Sliding Window**
- Count requests in rolling time window
- Smoothest rate limiting
- More memory intensive

**Fixed Window**
- Count requests per fixed period
- Simpler but allows burst at window edges

### Headers
```
X-RateLimit-Limit: 100          # Max requests per window
X-RateLimit-Remaining: 45       # Requests left
X-RateLimit-Reset: 1699900000   # Unix timestamp when window resets
Retry-After: 60                 # Seconds to wait (when limited)
```

### Response (429 Too Many Requests)
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded",
  "retry_after": 60
}
```

### Strategies
- Per API key
- Per user
- Per IP address
- Per endpoint (stricter for expensive operations)

## CORS (Cross-Origin Resource Sharing)

### Headers
```
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400
Access-Control-Allow-Credentials: true
```

### Preflight Request (OPTIONS)
Browser sends OPTIONS before actual request:
```
OPTIONS /api/users
Origin: https://app.example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Authorization
```

### Best Practices
- Never use `*` for credentials requests
- Whitelist specific origins
- Limit allowed headers
- Cache preflight responses (Max-Age)

## Input Validation

### Validate All Input
- Request body
- Query parameters
- Path parameters
- Headers

### Validation Rules
```python
# Length limits
name: str = Field(min_length=1, max_length=100)

# Format validation
email: EmailStr
url: HttpUrl

# Numeric bounds
age: int = Field(ge=0, le=150)
price: Decimal = Field(ge=0, decimal_places=2)

# Enum/allowed values
status: Literal["active", "inactive", "pending"]

# Pattern matching
phone: str = Field(pattern=r"^\+?[0-9]{10,15}$")
```

### Sanitization
- Escape HTML in output
- Parameterize SQL queries
- Validate file uploads (type, size)

## SQL Injection Prevention

### Bad (String concatenation)
```python
# VULNERABLE
query = f"SELECT * FROM users WHERE id = {user_id}"
```

### Good (Parameterized queries)
```python
# SQLAlchemy
db.query(User).filter(User.id == user_id)

# Raw SQL with params
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

## XSS Prevention

### Output Encoding
```python
# HTML escape user content
from markupsafe import escape
escaped = escape(user_input)
```

### Content Security Policy
```
Content-Security-Policy: default-src 'self'; script-src 'self'
```

### Response Headers
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

## Security Headers

### Essential Headers
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

## HTTPS Enforcement

### HSTS Header
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

### Redirect HTTP to HTTPS
```python
@app.middleware("http")
async def redirect_https(request, call_next):
    if request.url.scheme == "http":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url, status_code=301)
    return await call_next(request)
```

## Secrets Management

### Environment Variables
```bash
export API_SECRET_KEY=your-secret-key
export DATABASE_URL=postgresql://...
```

### Never Commit Secrets
```gitignore
.env
*.pem
*.key
credentials.json
```

### Secret Rotation
- Rotate API keys regularly
- Support multiple active keys during rotation
- Log key usage for audit

## OWASP Top 10 Checklist

1. **Broken Access Control** - Verify authorization on every request
2. **Cryptographic Failures** - Use strong encryption, HTTPS
3. **Injection** - Parameterize queries, validate input
4. **Insecure Design** - Threat modeling, security requirements
5. **Security Misconfiguration** - Secure defaults, minimize exposure
6. **Vulnerable Components** - Keep dependencies updated
7. **Authentication Failures** - Strong passwords, MFA, rate limit
8. **Data Integrity Failures** - Verify signatures, use checksums
9. **Logging Failures** - Log security events, protect logs
10. **SSRF** - Validate URLs, whitelist destinations

## Logging Security Events

### What to Log
- Authentication attempts (success/failure)
- Authorization failures
- Input validation failures
- Rate limit hits
- Unusual patterns

### What NOT to Log
- Passwords
- API keys/tokens
- PII (unless necessary)
- Full credit card numbers

### Log Format
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "warning",
  "event": "auth_failure",
  "ip": "192.168.1.1",
  "user_id": null,
  "endpoint": "/auth/login",
  "reason": "invalid_password"
}
```
