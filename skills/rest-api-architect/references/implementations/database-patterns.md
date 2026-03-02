# Database Patterns

## Repository Pattern

Abstracts data access, makes testing easier.

### Base Repository
```python
# app/repositories/base.py
from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseRepository(Generic[ModelType]):
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model

    async def get(self, id: int) -> Optional[ModelType]:
        return await self.db.get(self.model, id)

    async def get_multi(
        self, offset: int = 0, limit: int = 100
    ) -> List[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        db_obj = await self.get(id)
        if not db_obj:
            return None
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        db_obj = await self.get(id)
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.flush()
        return True

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        result = await self.db.execute(stmt)
        return result.scalar()
```

### Specific Repository
```python
# app/repositories/user_repository.py
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_with_count(
        self,
        offset: int = 0,
        limit: int = 20,
        status: str = None,
    ) -> Tuple[List[User], int]:
        # Base query
        query = select(User)
        count_query = select(func.count()).select_from(User)

        # Apply filters
        if status:
            query = query.where(User.status == status)
            count_query = count_query.where(User.status == status)

        # Get total count
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Get items
        query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, user_in: UserCreate) -> User:
        from app.core.security import get_password_hash
        db_obj = User(
            email=user_in.email,
            name=user_in.name,
            hashed_password=get_password_hash(user_in.password),
        )
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: int, user_in: UserUpdate) -> Optional[User]:
        update_data = user_in.model_dump(exclude_unset=True)
        return await super().update(id, update_data)
```

## SQLAlchemy Models

### Base Model
```python
# app/models/base.py
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

### User Model
```python
# app/models/user.py
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
```

## Alembic Migrations (Async)

### alembic.ini
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = driver://user:pass@localhost/dbname

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
```

### env.py (Async)
```python
# alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.config import settings
from app.models.base import Base
# Import all models to register them
from app.models import user  # noqa

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Commands
```bash
# Create migration
alembic revision --autogenerate -m "Add users table"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Query Patterns

### Filtering
```python
async def search_users(
    self,
    search: str = None,
    status: str = None,
    created_after: datetime = None,
) -> List[User]:
    query = select(User)

    if search:
        query = query.where(
            User.name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%")
        )
    if status:
        query = query.where(User.status == status)
    if created_after:
        query = query.where(User.created_at >= created_after)

    result = await self.db.execute(query)
    return list(result.scalars().all())
```

### Sorting
```python
from sqlalchemy import asc, desc

async def list_sorted(self, sort_by: str, sort_order: str = "asc"):
    query = select(User)

    column = getattr(User, sort_by, User.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(column))
    else:
        query = query.order_by(asc(column))

    result = await self.db.execute(query)
    return list(result.scalars().all())
```

### Upsert
```python
from sqlalchemy.dialects.postgresql import insert

async def upsert(self, data: dict) -> User:
    stmt = insert(User).values(**data)
    stmt = stmt.on_conflict_do_update(
        index_elements=[User.email],
        set_={
            "name": stmt.excluded.name,
            "updated_at": func.now(),
        }
    )
    await self.db.execute(stmt)
    await self.db.flush()

    # Fetch the upserted record
    return await self.get_by_email(data["email"])
```

### Eager Loading
```python
from sqlalchemy.orm import selectinload, joinedload

async def get_with_orders(self, user_id: int) -> User:
    stmt = (
        select(User)
        .options(selectinload(User.orders))
        .where(User.id == user_id)
    )
    result = await self.db.execute(stmt)
    return result.scalar_one_or_none()
```

## Connection Pool (Neon)

```python
# For Neon PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "ssl": "require",
        "server_settings": {
            "application_name": "my_api"
        }
    }
)
```

## Testing

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.models.base import Base

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    await engine.dispose()
```
