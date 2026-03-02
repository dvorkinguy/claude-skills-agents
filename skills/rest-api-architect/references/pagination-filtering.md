# Pagination and Filtering

## Pagination Patterns

### Offset-Based Pagination

Simple, widely used, good for small datasets.

**Request**
```
GET /users?page=2&limit=20
GET /users?offset=20&limit=20
```

**Response**
```json
{
  "items": [...],
  "total": 150,
  "page": 2,
  "page_size": 20,
  "pages": 8,
  "has_next": true,
  "has_prev": true
}
```

**Pros:**
- Easy to implement
- User can jump to any page
- Easy to understand

**Cons:**
- Inconsistent with real-time data changes
- Performance degrades on large offsets
- Duplicates/gaps when data changes

### Cursor-Based Pagination

Better for large datasets and real-time data.

**Request**
```
GET /users?cursor=eyJpZCI6MTAwfQ&limit=20
```

**Response**
```json
{
  "items": [...],
  "next_cursor": "eyJpZCI6MTIwfQ",
  "prev_cursor": "eyJpZCI6ODJ9",
  "has_next": true,
  "has_prev": true
}
```

**Cursor Content** (base64 encoded)
```json
{"id": 100, "created_at": "2024-01-15T10:30:00Z"}
```

**Pros:**
- Consistent results
- Efficient for large datasets
- Works with real-time data

**Cons:**
- Can't jump to arbitrary page
- More complex to implement
- Harder for users to understand

### Keyset Pagination

Similar to cursor, but explicit fields.

**Request**
```
GET /users?after_id=100&limit=20
GET /users?created_after=2024-01-15T10:30:00Z&limit=20
```

### Link Headers (RFC 5988)

```
Link: <https://api.example.com/users?page=3>; rel="next",
      <https://api.example.com/users?page=1>; rel="prev",
      <https://api.example.com/users?page=1>; rel="first",
      <https://api.example.com/users?page=8>; rel="last"
```

## Filtering

### Equality Filters
```
GET /users?status=active
GET /users?role=admin
GET /products?category=electronics
```

### Multiple Values
```
GET /users?status=active,pending
GET /users?id=1,2,3
```

### Comparison Operators
```
# Explicit operators
GET /products?price_gt=100           # Greater than
GET /products?price_gte=100          # Greater than or equal
GET /products?price_lt=500           # Less than
GET /products?price_lte=500          # Less than or equal

# Range
GET /products?price_min=100&price_max=500

# Date ranges
GET /orders?created_after=2024-01-01
GET /orders?created_before=2024-12-31
```

### Text Search
```
GET /users?search=john
GET /products?q=laptop
GET /articles?title_contains=guide
```

### Nested/Related Filters
```
GET /orders?user.status=active
GET /products?category.name=electronics
```

### Filter Objects (Complex)
```
GET /users?filter={"status":"active","age":{"$gte":18}}
```

## Sorting

### Single Field
```
GET /users?sort=name              # Ascending (default)
GET /users?sort=-name             # Descending (prefix -)
GET /users?sort=name:asc
GET /users?sort=name:desc
```

### Multiple Fields
```
GET /users?sort=status,-created_at
GET /users?sort=category,name:asc
```

### Default Sort
Always define a default sort for consistent pagination:
```python
def get_users(sort: str = "-created_at"):
    ...
```

## Field Selection

### Sparse Fieldsets
```
GET /users?fields=id,name,email
GET /users?fields[user]=id,name&fields[orders]=id,total
```

### Include Relations
```
GET /users?include=orders,profile
GET /orders?expand=user,products
```

### Exclude Fields
```
GET /users?exclude=password,internal_notes
```

## Implementation

### Query Parameters Model
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

class FilterParams(BaseModel):
    status: Optional[str] = None
    search: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

class SortParams(BaseModel):
    sort: str = "-created_at"

    def parse_sort(self) -> list[tuple[str, str]]:
        result = []
        for field in self.sort.split(","):
            if field.startswith("-"):
                result.append((field[1:], "desc"))
            else:
                result.append((field, "asc"))
        return result
```

### Response Model
```python
from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def create(cls, items: List[T], total: int, page: int, limit: int):
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=limit,
            pages=(total + limit - 1) // limit
        )
```

### SQL Query Builder
```python
def build_query(
    filters: FilterParams,
    sort: SortParams,
    pagination: PaginationParams
):
    query = select(User)

    # Apply filters
    if filters.status:
        query = query.where(User.status == filters.status)
    if filters.search:
        query = query.where(User.name.ilike(f"%{filters.search}%"))
    if filters.created_after:
        query = query.where(User.created_at >= filters.created_after)

    # Apply sorting
    for field, direction in sort.parse_sort():
        column = getattr(User, field)
        query = query.order_by(
            column.desc() if direction == "desc" else column.asc()
        )

    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.limit)

    return query
```

## Best Practices

1. **Always paginate** - Never return unbounded lists
2. **Default limits** - Set sensible defaults (20-50)
3. **Maximum limits** - Cap at reasonable max (100-1000)
4. **Consistent sorting** - Always include tie-breaker (ID)
5. **Document filters** - List all available filters in docs
6. **Validate input** - Reject invalid sort fields, filter values
7. **Performance** - Index columns used for filtering/sorting
