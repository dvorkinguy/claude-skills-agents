# API Caching

## Cache-Control Header

### Directives

```
Cache-Control: max-age=3600                    # Cache for 1 hour
Cache-Control: max-age=3600, public            # CDN can cache
Cache-Control: max-age=3600, private           # Only browser cache
Cache-Control: no-cache                        # Validate before use
Cache-Control: no-store                        # Never cache
Cache-Control: must-revalidate                 # Revalidate when stale
Cache-Control: stale-while-revalidate=60       # Serve stale while updating
```

### Common Patterns

**Public, cacheable content:**
```
Cache-Control: public, max-age=3600
```

**User-specific content:**
```
Cache-Control: private, max-age=300
```

**Never cache (sensitive data):**
```
Cache-Control: no-store
```

**Cache but always validate:**
```
Cache-Control: no-cache
# or
Cache-Control: max-age=0, must-revalidate
```

## ETags

### Strong ETag
Exact byte-for-byte match.
```
ETag: "abc123def456"
```

### Weak ETag
Semantically equivalent.
```
ETag: W/"abc123"
```

### Generating ETags
```python
import hashlib
import json

def generate_etag(data: dict) -> str:
    content = json.dumps(data, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()

# From database
def etag_from_updated_at(updated_at: datetime) -> str:
    return f'"{updated_at.timestamp()}"'
```

## Conditional Requests

### If-None-Match (ETag validation)

**Request:**
```
GET /users/123
If-None-Match: "abc123"
```

**Response (not modified):**
```
304 Not Modified
ETag: "abc123"
```

**Response (modified):**
```
200 OK
ETag: "xyz789"

{...new data...}
```

### If-Modified-Since (Date validation)

**Request:**
```
GET /users/123
If-Modified-Since: Wed, 15 Nov 2023 12:45:26 GMT
```

**Response:**
```
304 Not Modified
Last-Modified: Wed, 15 Nov 2023 12:45:26 GMT
```

### If-Match (Optimistic locking)

**Request:**
```
PUT /users/123
If-Match: "abc123"

{...updated data...}
```

**Response (conflict):**
```
412 Precondition Failed
```

## Implementation

### FastAPI Example
```python
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

@app.get("/users/{user_id}")
async def get_user(user_id: int, request: Request, response: Response):
    user = await get_user_from_db(user_id)

    # Generate ETag
    etag = generate_etag(user.dict())

    # Check If-None-Match
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match == etag:
        return Response(status_code=304)

    # Set caching headers
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "private, max-age=300"
    response.headers["Last-Modified"] = user.updated_at.strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

    return user
```

### Middleware Approach
```python
@app.middleware("http")
async def cache_middleware(request: Request, call_next):
    response = await call_next(request)

    # Skip for non-GET or errors
    if request.method != "GET" or response.status_code >= 400:
        return response

    # Add default cache headers if not set
    if "Cache-Control" not in response.headers:
        response.headers["Cache-Control"] = "private, max-age=60"

    return response
```

## Cache Invalidation

### Time-Based (TTL)
```
Cache-Control: max-age=3600
```

### Event-Based
Invalidate on data change:
```python
async def update_user(user_id: int, data: dict):
    user = await update_in_db(user_id, data)
    await cache.delete(f"user:{user_id}")
    return user
```

### Surrogate Keys
Tag cached responses for bulk invalidation:
```
Surrogate-Key: user-123 users all-users
```

Invalidate:
```
PURGE /
Surrogate-Key: user-123
```

## Caching Strategies by Resource Type

### Static Reference Data
```
# Countries, categories, etc.
Cache-Control: public, max-age=86400  # 24 hours
```

### User Data
```
Cache-Control: private, max-age=300  # 5 minutes
```

### Real-Time Data
```
Cache-Control: no-cache
# Or short TTL
Cache-Control: max-age=10
```

### Sensitive Data
```
Cache-Control: no-store
```

## CDN Caching

### Vary Header
Tell CDN what varies the response:
```
Vary: Accept-Encoding, Authorization
```

### CDN-Specific Headers
```
# Cloudflare
CDN-Cache-Control: max-age=3600

# Fastly
Surrogate-Control: max-age=3600
```

### Cache Key
Include relevant query params:
```
# Same cache for different order
/users?page=1&limit=20
/users?limit=20&page=1

# Different cache
/users?page=1
/users?page=2
```

## Best Practices

1. **Always set Cache-Control** - Explicit is better than implicit
2. **Use ETags for dynamic content** - Efficient validation
3. **Private for user data** - Prevent CDN caching personal info
4. **Vary header** - Include all factors that vary response
5. **Stale-while-revalidate** - Better UX during revalidation
6. **Short TTL + revalidation** - Balance freshness and performance
7. **Invalidate on writes** - Keep cache consistent
8. **Monitor cache hit rate** - Optimize caching strategy
