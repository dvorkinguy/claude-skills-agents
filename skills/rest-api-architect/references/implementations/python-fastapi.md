# FastAPI Implementation Guide

## Project Structure

```
app/
├── __init__.py
├── main.py                 # FastAPI app entry point
├── config.py               # Settings/configuration
├── core/
│   ├── __init__.py
│   ├── database.py         # Database connection
│   ├── dependencies.py     # FastAPI dependencies
│   ├── exceptions.py       # Custom exceptions
│   └── security.py         # Auth utilities
├── models/                 # SQLAlchemy models
│   ├── __init__.py
│   ├── base.py
│   └── user.py
├── schemas/                # Pydantic schemas
│   ├── __init__.py
│   ├── user.py
│   └── common.py
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── router.py       # Main v1 router
│       ├── users.py
│       └── health.py
├── services/               # Business logic
│   ├── __init__.py
│   └── user_service.py
└── repositories/           # Data access
    ├── __init__.py
    └── user_repository.py
```

## Main Application

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import api_router
from app.core.database import engine
from app.core.exceptions import register_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
register_exception_handlers(app)

# Routes
app.include_router(api_router, prefix="/api/v1")
```

## Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "My API"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

## Async Database (SQLAlchemy 2.0)

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Dependencies

```python
# app/core/dependencies.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.core.database import get_db
from app.config import settings
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Database dependency
DB = Annotated[AsyncSession, Depends(get_db)]

async def get_current_user(
    db: DB,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
```

## Pydantic Schemas

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# app/schemas/common.py
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit
```

## API Routes

```python
# app/api/v1/users.py
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from app.core.dependencies import DB, CurrentUser
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import PaginatedResponse, PaginationParams
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    db: DB,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = None,
):
    """List all users with pagination."""
    service = UserService(db)
    pagination = PaginationParams(page=page, limit=limit)
    return await service.list_users(pagination, status=status)

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(db: DB, user_in: UserCreate):
    """Create a new user."""
    service = UserService(db)
    return await service.create_user(user_in)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(db: DB, user_id: int):
    """Get user by ID."""
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    db: DB,
    user_id: int,
    user_in: UserUpdate,
    current_user: CurrentUser,
):
    """Update user (requires authentication)."""
    service = UserService(db)
    user = await service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: DB, user_id: int, current_user: CurrentUser):
    """Delete user (requires authentication)."""
    service = UserService(db)
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
```

## Router Aggregation

```python
# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1 import users, health, auth

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
```

## Exception Handling

```python
# app/core/exceptions.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

class APIError(Exception):
    def __init__(self, status_code: int, detail: str, error_type: str = None):
        self.status_code = status_code
        self.detail = detail
        self.error_type = error_type or "api_error"

class NotFoundError(APIError):
    def __init__(self, resource: str, id: any):
        super().__init__(404, f"{resource} with ID {id} not found", "not_found")

class ConflictError(APIError):
    def __init__(self, detail: str):
        super().__init__(409, detail, "conflict")

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": f"https://api.example.com/errors/{exc.error_type}",
                "title": exc.error_type.replace("_", " ").title(),
                "status": exc.status_code,
                "detail": exc.detail,
                "instance": str(request.url.path),
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "type": "https://api.example.com/errors/validation",
                "title": "Validation Error",
                "status": 422,
                "detail": "Request validation failed",
                "errors": exc.errors(),
            },
        )
```

## Service Layer

```python
# app/services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.common import PaginationParams, PaginatedResponse

class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def list_users(
        self, pagination: PaginationParams, status: str = None
    ) -> PaginatedResponse:
        users, total = await self.repo.list_with_count(
            offset=pagination.offset,
            limit=pagination.limit,
            status=status,
        )
        return PaginatedResponse(
            items=users,
            total=total,
            page=pagination.page,
            page_size=pagination.limit,
            pages=(total + pagination.limit - 1) // pagination.limit,
        )

    async def create_user(self, user_in: UserCreate):
        return await self.repo.create(user_in)

    async def get_user(self, user_id: int):
        return await self.repo.get(user_id)

    async def update_user(self, user_id: int, user_in: UserUpdate):
        return await self.repo.update(user_id, user_in)

    async def delete_user(self, user_id: int) -> bool:
        return await self.repo.delete(user_id)
```

## Health Check

```python
# app/api/v1/health.py
from fastapi import APIRouter
from sqlalchemy import text
from app.core.dependencies import DB

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/health/db")
async def health_db(db: DB):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
```

## Running the App

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```
