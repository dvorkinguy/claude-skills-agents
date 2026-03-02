# Rate Limiting Strategies Pattern

Managing API quotas across multiple trade data sources.

## API Rate Limits Overview

| API | Free Tier | Paid Tier | Reset Period |
|-----|-----------|-----------|--------------|
| UN Comtrade | 500 records/call | 250K records/call | Per request |
| WITS | Undocumented | N/A | Unknown |
| UK Trade Tariff | Undocumented | N/A | Unknown |
| Global Trade Alert | Limited | Research access | Unknown |
| TariffsAPI (US) | Varies | Higher limits | Monthly |

---

## Core Rate Limiting Implementation

### Token Bucket Algorithm

```python
import time
import asyncio
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime, timedelta
import threading

@dataclass
class RateLimitConfig:
    """Configuration for an API's rate limits."""
    requests_per_second: float = 1.0
    requests_per_minute: float = 60.0
    requests_per_hour: float = 1000.0
    requests_per_day: float = 10000.0
    max_burst: int = 10
    retry_after_seconds: float = 60.0


class TokenBucket:
    """Token bucket rate limiter."""

    def __init__(
        self,
        rate: float,          # Tokens per second
        capacity: int = 10    # Max burst size
    ):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens.

        Returns True if tokens acquired, False if would exceed limit.
        """
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update

            # Add tokens based on elapsed time
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    async def acquire_async(self, tokens: int = 1) -> None:
        """Async version that waits until tokens available."""
        while not self.acquire(tokens):
            wait_time = (tokens - self.tokens) / self.rate
            await asyncio.sleep(min(wait_time, 1.0))

    def time_until_available(self, tokens: int = 1) -> float:
        """Seconds until tokens will be available."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            current = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )

            if current >= tokens:
                return 0.0
            return (tokens - current) / self.rate


class MultiLevelRateLimiter:
    """Rate limiter with multiple time windows."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.buckets = {
            'second': TokenBucket(
                rate=config.requests_per_second,
                capacity=config.max_burst
            ),
            'minute': TokenBucket(
                rate=config.requests_per_minute / 60,
                capacity=int(config.requests_per_minute / 10)
            ),
            'hour': TokenBucket(
                rate=config.requests_per_hour / 3600,
                capacity=int(config.requests_per_hour / 60)
            ),
            'day': TokenBucket(
                rate=config.requests_per_day / 86400,
                capacity=int(config.requests_per_day / 24)
            ),
        }

    def acquire(self) -> bool:
        """Acquire from all buckets."""
        return all(bucket.acquire() for bucket in self.buckets.values())

    async def acquire_async(self) -> None:
        """Wait until all buckets allow request."""
        for bucket in self.buckets.values():
            await bucket.acquire_async()

    def time_until_available(self) -> float:
        """Max wait time across all buckets."""
        return max(
            bucket.time_until_available()
            for bucket in self.buckets.values()
        )


# Usage
config = RateLimitConfig(
    requests_per_second=2,
    requests_per_minute=100,
    requests_per_hour=1000,
    requests_per_day=5000,
    max_burst=5
)

limiter = MultiLevelRateLimiter(config)

async def make_request():
    await limiter.acquire_async()
    # Make API call
    pass
```

---

## Multi-Source Rate Manager

```python
from typing import Dict, Callable, Any
from enum import Enum
import asyncio

class APISource(Enum):
    COMTRADE = "comtrade"
    WITS = "wits"
    UK_TARIFF = "uk_tariff"
    GTA = "gta"
    TARIFFS_API = "tariffs_api"


class MultiSourceRateManager:
    """Manage rate limits across multiple APIs."""

    # Default configurations per source
    DEFAULT_CONFIGS = {
        APISource.COMTRADE: RateLimitConfig(
            requests_per_second=1,
            requests_per_minute=30,
            requests_per_hour=500,
            max_burst=3
        ),
        APISource.WITS: RateLimitConfig(
            requests_per_second=0.5,  # Conservative for undocumented
            requests_per_minute=20,
            requests_per_hour=200,
            max_burst=2
        ),
        APISource.UK_TARIFF: RateLimitConfig(
            requests_per_second=2,
            requests_per_minute=60,
            requests_per_hour=500,
            max_burst=5
        ),
        APISource.GTA: RateLimitConfig(
            requests_per_second=0.25,  # Very conservative
            requests_per_minute=10,
            requests_per_hour=50,
            max_burst=1
        ),
        APISource.TARIFFS_API: RateLimitConfig(
            requests_per_second=5,
            requests_per_minute=100,
            requests_per_hour=1000,
            max_burst=10
        ),
    }

    def __init__(self, custom_configs: Dict[APISource, RateLimitConfig] = None):
        configs = {**self.DEFAULT_CONFIGS}
        if custom_configs:
            configs.update(custom_configs)

        self.limiters = {
            source: MultiLevelRateLimiter(config)
            for source, config in configs.items()
        }
        self._request_counts = {source: 0 for source in APISource}
        self._error_counts = {source: 0 for source in APISource}
        self._backoff_until = {source: None for source in APISource}

    async def acquire(self, source: APISource) -> None:
        """Wait for rate limit clearance for a source."""
        # Check if in backoff
        backoff = self._backoff_until.get(source)
        if backoff and datetime.utcnow() < backoff:
            wait = (backoff - datetime.utcnow()).total_seconds()
            await asyncio.sleep(wait)

        # Acquire from limiter
        await self.limiters[source].acquire_async()
        self._request_counts[source] += 1

    def record_error(self, source: APISource, status_code: int = None):
        """Record an API error and potentially trigger backoff."""
        self._error_counts[source] += 1

        # Backoff on rate limit errors
        if status_code == 429:
            backoff_seconds = self.DEFAULT_CONFIGS[source].retry_after_seconds
            self._backoff_until[source] = (
                datetime.utcnow() + timedelta(seconds=backoff_seconds)
            )

    def get_stats(self) -> Dict[str, Dict]:
        """Get usage statistics."""
        return {
            source.value: {
                'requests': self._request_counts[source],
                'errors': self._error_counts[source],
                'wait_time': self.limiters[source].time_until_available()
            }
            for source in APISource
        }

    def get_best_available_source(
        self,
        sources: list[APISource]
    ) -> Optional[APISource]:
        """
        Get the source with shortest wait time.

        Useful for fallback strategies.
        """
        available = []
        for source in sources:
            wait = self.limiters[source].time_until_available()
            backoff = self._backoff_until.get(source)
            if backoff and datetime.utcnow() < backoff:
                wait = max(wait, (backoff - datetime.utcnow()).total_seconds())
            available.append((source, wait))

        available.sort(key=lambda x: x[1])
        return available[0][0] if available else None


# Usage
manager = MultiSourceRateManager()

async def fetch_trade_data(product: str, source: APISource):
    await manager.acquire(source)

    try:
        # Make API call
        response = await call_api(source, product)
        return response
    except RateLimitError:
        manager.record_error(source, 429)
        raise


async def fetch_with_fallback(product: str):
    """Try sources in order of availability."""
    sources = [APISource.COMTRADE, APISource.WITS, APISource.UK_TARIFF]

    best = manager.get_best_available_source(sources)
    if best:
        return await fetch_trade_data(product, best)

    raise Exception("All sources exhausted")
```

---

## Caching to Reduce API Calls

```python
from functools import wraps
from typing import Callable, Any, Optional
import hashlib
import json
import time
from datetime import datetime, timedelta
import sqlite3

class APICache:
    """SQLite-based cache for API responses."""

    def __init__(self, db_path: str = "trade_cache.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                source TEXT,
                created_at TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
        self.conn.commit()

    def _make_key(self, **kwargs) -> str:
        """Create cache key from parameters."""
        key_str = json.dumps(kwargs, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get(self, **kwargs) -> Optional[dict]:
        """Get cached value if not expired."""
        key = self._make_key(**kwargs)
        cursor = self.conn.execute(
            "SELECT value, expires_at FROM cache WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()

        if row:
            value, expires_at = row
            if datetime.fromisoformat(expires_at) > datetime.utcnow():
                return json.loads(value)
            else:
                # Expired - delete
                self.conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                self.conn.commit()

        return None

    def set(
        self,
        value: dict,
        ttl_hours: int = 24,
        source: str = "",
        **kwargs
    ):
        """Cache a value with TTL."""
        key = self._make_key(**kwargs)
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

        self.conn.execute("""
            INSERT OR REPLACE INTO cache (key, value, source, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            key,
            json.dumps(value),
            source,
            datetime.utcnow().isoformat(),
            expires_at.isoformat()
        ))
        self.conn.commit()

    def clear_expired(self):
        """Remove all expired entries."""
        self.conn.execute(
            "DELETE FROM cache WHERE expires_at < ?",
            (datetime.utcnow().isoformat(),)
        )
        self.conn.commit()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        cursor = self.conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN expires_at > ? THEN 1 ELSE 0 END) as valid
            FROM cache
        """, (datetime.utcnow().isoformat(),))
        row = cursor.fetchone()
        return {
            'total_entries': row[0],
            'valid_entries': row[1],
            'expired_entries': row[0] - row[1]
        }


def cached(cache: APICache, ttl_hours: int = 24):
    """Decorator to cache API responses."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try cache first
            cached_value = cache.get(**kwargs)
            if cached_value is not None:
                return cached_value

            # Call API
            result = await func(*args, **kwargs)

            # Cache result
            cache.set(result, ttl_hours=ttl_hours, source=func.__name__, **kwargs)

            return result
        return wrapper
    return decorator


# Usage
cache = APICache()

@cached(cache, ttl_hours=72)  # Trade data doesn't change often
async def get_comtrade_data(
    reporter: str,
    partner: str,
    product: str,
    year: int
) -> dict:
    # This only runs if not in cache
    await rate_manager.acquire(APISource.COMTRADE)
    return await comtrade_api.get_data(reporter, partner, product, year)
```

---

## Bulk Download Strategy

For large data needs, prefer bulk downloads over individual API calls:

```python
import asyncio
from pathlib import Path
import pandas as pd

class BulkDownloadManager:
    """Manage bulk data downloads to reduce API calls."""

    def __init__(self, data_dir: str = "./trade_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    async def download_comtrade_bulk(
        self,
        reporter: str,
        year: int,
        subscription_key: str
    ) -> Path:
        """
        Download full year of data for a reporter.

        UN Comtrade offers bulk downloads for subscribers.
        """
        import comtradeapicall

        filepath = self.data_dir / f"comtrade_{reporter}_{year}.parquet"

        if filepath.exists():
            # Check if recent enough
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
            if datetime.utcnow() - mtime < timedelta(days=30):
                return filepath

        # Download bulk file
        data = comtradeapicall.bulkDownloadFinalFile(
            subscription_key=subscription_key,
            typeCode='C',
            freqCode='A',
            clCode='HS',
            period=str(year),
            reporterCode=reporter,
            decompress=True
        )

        if data is not None:
            data.to_parquet(filepath)
            return filepath

        raise Exception(f"Bulk download failed for {reporter}/{year}")

    def query_local(
        self,
        reporter: str,
        year: int,
        partner: str = None,
        product: str = None
    ) -> pd.DataFrame:
        """Query locally cached bulk data."""
        filepath = self.data_dir / f"comtrade_{reporter}_{year}.parquet"

        if not filepath.exists():
            raise FileNotFoundError(f"No local data for {reporter}/{year}")

        df = pd.read_parquet(filepath)

        # Filter
        if partner:
            df = df[df['partnerCode'] == partner]
        if product:
            df = df[df['cmdCode'].str.startswith(product)]

        return df


# Strategy: Download bulk data for major reporters
async def prefetch_major_reporters(manager: BulkDownloadManager, key: str):
    """Pre-download data for top trading nations."""
    major_reporters = ['USA', 'CHN', 'DEU', 'JPN', 'GBR', 'FRA']
    current_year = datetime.utcnow().year - 1  # Latest complete year

    for reporter in major_reporters:
        try:
            await manager.download_comtrade_bulk(reporter, current_year, key)
            print(f"Downloaded {reporter} {current_year}")
            await asyncio.sleep(5)  # Be respectful between large downloads
        except Exception as e:
            print(f"Failed {reporter}: {e}")
```

---

## Retry Logic with Exponential Backoff

```python
import random
from typing import TypeVar, Callable
from functools import wraps

T = TypeVar('T')

class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


def with_retry(
    config: RetryConfig = None,
    retryable_exceptions: tuple = (Exception,)
):
    """Decorator for retry with exponential backoff."""
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == config.max_attempts - 1:
                        break

                    # Calculate delay
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )

                    # Add jitter
                    if config.jitter:
                        delay = delay * (0.5 + random.random())

                    print(f"Attempt {attempt + 1} failed, retrying in {delay:.1f}s")
                    await asyncio.sleep(delay)

            raise last_exception

        return wrapper
    return decorator


# Usage
@with_retry(
    config=RetryConfig(max_attempts=3, base_delay=2.0),
    retryable_exceptions=(ConnectionError, TimeoutError, RateLimitError)
)
async def fetch_with_retry(source: APISource, params: dict):
    await rate_manager.acquire(source)
    return await api_call(source, params)
```

---

## Best Practices

1. **Know your limits** - Read API docs carefully, test conservatively
2. **Cache aggressively** - Trade data is relatively static
3. **Use bulk downloads** - For large datasets, one download beats many calls
4. **Implement backoff** - Respect 429 responses with exponential backoff
5. **Monitor usage** - Track requests per source, catch limits early
6. **Prefer local data** - Check cache/local files before API calls
7. **Stagger requests** - Don't burst all calls at once
8. **Have fallbacks** - If one source is limited, try another
