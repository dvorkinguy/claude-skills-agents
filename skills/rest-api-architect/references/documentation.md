# API Documentation

## OpenAPI Specification (OAS)

### Basic Structure (OpenAPI 3.1)
```yaml
openapi: 3.1.0
info:
  title: My API
  version: 1.0.0
  description: API for managing users
  contact:
    email: api@example.com
  license:
    name: MIT

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://staging-api.example.com/v1
    description: Staging

paths:
  /users:
    get:
      summary: List users
      operationId: listUsers
      tags: [Users]
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/LimitParam'
      responses:
        '200':
          description: List of users
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
          format: email
      required: [id, name, email]

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

### Path Operations
```yaml
/users/{userId}:
  get:
    summary: Get user by ID
    operationId: getUserById
    tags: [Users]
    parameters:
      - name: userId
        in: path
        required: true
        schema:
          type: integer
    responses:
      '200':
        description: User found
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      '404':
        $ref: '#/components/responses/NotFound'
```

### Request Body
```yaml
post:
  summary: Create user
  requestBody:
    required: true
    content:
      application/json:
        schema:
          type: object
          properties:
            name:
              type: string
              minLength: 1
              maxLength: 100
            email:
              type: string
              format: email
          required: [name, email]
        example:
          name: John Doe
          email: john@example.com
```

### Reusable Components
```yaml
components:
  parameters:
    PageParam:
      name: page
      in: query
      schema:
        type: integer
        default: 1
        minimum: 1
    LimitParam:
      name: limit
      in: query
      schema:
        type: integer
        default: 20
        minimum: 1
        maximum: 100

  responses:
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

  schemas:
    Error:
      type: object
      properties:
        error:
          type: string
        message:
          type: string
```

## API Versioning

### URL Path (Recommended)
```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

**Pros:** Clear, easy to route, cacheable
**Cons:** URL changes between versions

### Header
```
Accept: application/vnd.example.v1+json
```

**Pros:** Clean URLs
**Cons:** Harder to test, not cacheable

### Query Parameter
```
https://api.example.com/users?version=1
```

**Pros:** Easy to implement
**Cons:** Not RESTful, affects caching

### Best Practices
- Major versions only (v1, v2)
- Support 2-3 versions simultaneously
- Deprecate with 6-12 month notice
- Use Sunset header for deprecation

```
Sunset: Sat, 01 Jun 2025 00:00:00 GMT
Deprecation: true
Link: <https://api.example.com/v2/users>; rel="successor-version"
```

## Documentation Tools

### Swagger UI
Interactive API explorer from OpenAPI spec.

**FastAPI** (built-in):
```
GET /docs      # Swagger UI
GET /redoc     # ReDoc
GET /openapi.json
```

### ReDoc
Clean, responsive documentation.

### Postman
- Import OpenAPI spec
- Generate collections
- Create examples and tests

## Documentation Best Practices

### 1. Clear Descriptions
```yaml
summary: Create a new user account
description: |
  Creates a new user with the provided information.

  **Note:** Email must be unique across all users.

  Returns the created user with assigned ID.
```

### 2. Examples
```yaml
schema:
  $ref: '#/components/schemas/User'
examples:
  basic:
    summary: Basic user
    value:
      id: 123
      name: John Doe
      email: john@example.com
  admin:
    summary: Admin user
    value:
      id: 1
      name: Admin
      email: admin@example.com
      role: admin
```

### 3. Error Documentation
Document all possible error responses:
```yaml
responses:
  '200':
    description: Success
  '400':
    description: Invalid input
  '401':
    description: Authentication required
  '403':
    description: Permission denied
  '404':
    description: User not found
  '422':
    description: Validation error
```

### 4. Authentication Instructions
```yaml
security:
  - bearerAuth: []

# With description in securitySchemes
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        Get token from POST /auth/login
        Include in header: Authorization: Bearer <token>
```

### 5. Rate Limit Documentation
```yaml
x-rateLimit:
  limit: 100
  window: 60
  description: 100 requests per minute
```

## Changelog

### Format
```markdown
# Changelog

## [2.0.0] - 2024-01-15
### Breaking Changes
- Removed deprecated `GET /users/list` endpoint
- Changed `user_id` to `id` in response

### Added
- New `PATCH /users/{id}` endpoint
- Filtering by status

### Fixed
- Pagination count accuracy

## [1.1.0] - 2023-12-01
### Added
- Rate limiting headers
```

### Versioning Semantics
- **Major (v2):** Breaking changes
- **Minor (v1.1):** New features, backward compatible
- **Patch (v1.0.1):** Bug fixes
