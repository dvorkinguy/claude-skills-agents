# REST API Design Fundamentals

## Core Principles

### 1. Resources, Not Actions
URLs represent resources (nouns), not actions (verbs).

```
# Good
GET  /users
POST /orders
GET  /products/123

# Bad
GET  /getUsers
POST /createOrder
GET  /fetchProduct?id=123
```

### 2. HTTP Methods for Actions
Use HTTP methods to indicate the action:

| Method | CRUD | Collection `/users` | Item `/users/{id}` |
|--------|------|---------------------|-------------------|
| GET | Read | List all | Get one |
| POST | Create | Create new | - |
| PUT | Replace | Replace all | Replace one |
| PATCH | Update | - | Partial update |
| DELETE | Delete | Delete all | Delete one |

### 3. Plural Resource Names
Use plural nouns for consistency:
```
/users        # not /user
/orders       # not /order
/categories   # not /category
```

### 4. Hierarchical Resources
Express relationships through nesting:
```
GET /users/{userId}/orders              # User's orders
GET /users/{userId}/orders/{orderId}    # Specific order
POST /users/{userId}/addresses          # Add address
```

Limit nesting to 2-3 levels. Beyond that, use query params:
```
# Instead of deeply nested
GET /companies/{id}/departments/{id}/employees/{id}/tasks

# Use flat with filters
GET /tasks?employee_id=123
```

## URL Design Patterns

### Path Parameters
Identify specific resources:
```
GET /users/123         # User with ID 123
GET /products/sku-456  # Product by SKU
```

### Query Parameters
Filter, sort, paginate collections:
```
GET /users?status=active           # Filter
GET /users?sort=created_at:desc    # Sort
GET /users?page=2&limit=20         # Paginate
GET /users?fields=id,name,email    # Sparse fields
```

### Common Query Patterns
```
# Filtering
?status=active
?status=active,pending         # Multiple values
?created_after=2024-01-01
?price_min=10&price_max=100

# Sorting
?sort=name                     # Ascending
?sort=-name                    # Descending (prefix -)
?sort=name:asc                 # Explicit direction
?sort=category,name            # Multiple fields

# Pagination
?page=1&limit=20               # Offset-based
?cursor=abc123&limit=20        # Cursor-based
?offset=40&limit=20            # Offset explicit

# Field Selection
?fields=id,name,email
?include=orders,addresses      # Include relations
?expand=author                 # Expand nested
```

## Request/Response Design

### Request Body (POST/PUT/PATCH)
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "admin"
}
```

### Response Body (Single Resource)
```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "admin",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Response Body (Collection)
```json
{
  "items": [
    {"id": 1, "name": "User 1"},
    {"id": 2, "name": "User 2"}
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "pages": 8
}
```

## Naming Conventions

### URL Paths
- Use lowercase
- Use hyphens for multi-word: `/user-profiles`
- No trailing slashes: `/users` not `/users/`
- No file extensions: `/users` not `/users.json`

### JSON Fields
- Use `snake_case`: `created_at`, `user_id`
- Or `camelCase`: `createdAt`, `userId`
- Be consistent throughout API

### Dates/Times
Use ISO 8601 format with timezone:
```
"created_at": "2024-01-15T10:30:00Z"
"expires_at": "2024-01-15T10:30:00+02:00"
```

## Idempotency

### Idempotent Methods
Multiple identical requests produce same result:
- GET, PUT, DELETE are idempotent
- POST is NOT idempotent

### Idempotency Keys
For non-idempotent operations, use idempotency keys:
```
POST /orders
Idempotency-Key: unique-request-id-123
```

## HATEOAS (Optional)

Hypermedia As The Engine Of Application State - include links:
```json
{
  "id": 123,
  "name": "John",
  "_links": {
    "self": {"href": "/users/123"},
    "orders": {"href": "/users/123/orders"},
    "update": {"href": "/users/123", "method": "PATCH"}
  }
}
```

## Content Negotiation

### Request Headers
```
Accept: application/json
Content-Type: application/json
```

### Response Headers
```
Content-Type: application/json; charset=utf-8
```
