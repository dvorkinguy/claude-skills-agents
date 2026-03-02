# Multi-Source Aggregation Pattern

Combining data from multiple trade data APIs to get comprehensive coverage.

## Why Aggregate Multiple Sources?

| Challenge | Solution |
|-----------|----------|
| No single API has all data | Combine Comtrade (volumes) + WITS (tariffs) |
| Coverage gaps | One source may have data another lacks |
| Validation | Cross-check figures between sources |
| Different perspectives | Reporter vs partner data |

---

## Source Priority Matrix

For different data needs, prioritize sources accordingly:

### Trade Volumes (Imports/Exports)

| Priority | Source | Strength |
|----------|--------|----------|
| 1 | UN Comtrade | Most comprehensive, standardized |
| 2 | WITS TRAINS | Good coverage, tariff context |
| 3 | National sources | Most current, country-specific |

### Tariff Rates

| Priority | Source | Strength |
|----------|--------|----------|
| 1 | WITS/UNCTAD | Global MFN + preferential |
| 2 | UK Trade Tariff | UK-specific, very current |
| 3 | TariffsAPI (US) | US-specific, Section 301 |
| 4 | National sources | Most authoritative |

### Policy Monitoring

| Priority | Source | Strength |
|----------|--------|----------|
| 1 | Global Trade Alert | Comprehensive intervention tracking |
| 2 | WTO notifications | Official, legally binding |
| 3 | News sources | Most current events |

---

## Aggregation Architecture

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class TradeDataPoint:
    """Standardized trade data record."""
    reporter: str          # ISO3 country code
    partner: str           # ISO3 country code
    product: str           # HS code
    year: int
    flow: str              # 'import' or 'export'
    value_usd: float
    quantity: Optional[float] = None
    quantity_unit: Optional[str] = None
    source: str = ""
    retrieved_at: datetime = None

    def __post_init__(self):
        if self.retrieved_at is None:
            self.retrieved_at = datetime.utcnow()


class TradeDataSource(ABC):
    """Abstract base class for trade data sources."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """Lower number = higher priority."""
        pass

    @abstractmethod
    async def get_trade_data(
        self,
        reporter: str,
        partner: str,
        product: str,
        year: int,
        flow: str
    ) -> Optional[TradeDataPoint]:
        pass


class ComtradeSource(TradeDataSource):
    """UN Comtrade as primary source."""

    name = "comtrade"
    priority = 1

    def __init__(self, subscription_key: str):
        self.key = subscription_key

    async def get_trade_data(
        self,
        reporter: str,
        partner: str,
        product: str,
        year: int,
        flow: str
    ) -> Optional[TradeDataPoint]:
        # Implementation using comtradeapicall
        import comtradeapicall

        flow_code = 'M' if flow == 'import' else 'X'

        data = comtradeapicall.getFinalData(
            subscription_key=self.key,
            typeCode='C',
            freqCode='A',
            clCode='HS',
            period=str(year),
            reporterCode=reporter,
            cmdCode=product,
            flowCode=flow_code,
            partnerCode=partner,
            partner2Code=None
        )

        if data is not None and len(data) > 0:
            row = data.iloc[0]
            return TradeDataPoint(
                reporter=reporter,
                partner=partner,
                product=product,
                year=year,
                flow=flow,
                value_usd=row.get('primaryValue', 0),
                quantity=row.get('qty'),
                quantity_unit=row.get('qtyUnitAbbr'),
                source=self.name
            )
        return None


class WITSSource(TradeDataSource):
    """World Bank WITS as secondary source."""

    name = "wits"
    priority = 2

    async def get_trade_data(
        self,
        reporter: str,
        partner: str,
        product: str,
        year: int,
        flow: str
    ) -> Optional[TradeDataPoint]:
        import requests

        indicator = 'MPRT-TRD-VL' if flow == 'import' else 'XPRT-TRD-VL'

        url = (
            f"https://wits.worldbank.org/API/V1/SDMX/V21/"
            f"datasource/tradestats-trade/reporter/{reporter.lower()}/"
            f"year/{year}/partner/{partner.lower()}/product/{product}/"
            f"indicator/{indicator}"
        )

        response = requests.get(url, params={'format': 'JSON'})
        if response.status_code == 200:
            # Parse SDMX response (simplified)
            data = response.json()
            value = self._extract_value(data)
            if value is not None:
                return TradeDataPoint(
                    reporter=reporter,
                    partner=partner,
                    product=product,
                    year=year,
                    flow=flow,
                    value_usd=value * 1000,  # WITS reports in thousands
                    source=self.name
                )
        return None

    def _extract_value(self, sdmx_data: dict) -> Optional[float]:
        """Extract value from SDMX response."""
        try:
            datasets = sdmx_data.get('dataSets', [])
            if datasets:
                obs = datasets[0].get('observations', {})
                if obs:
                    first_key = list(obs.keys())[0]
                    return obs[first_key][0]
        except (KeyError, IndexError):
            pass
        return None


class MultiSourceAggregator:
    """Aggregates data from multiple sources with fallback."""

    def __init__(self, sources: List[TradeDataSource]):
        # Sort by priority
        self.sources = sorted(sources, key=lambda s: s.priority)
        self.cache = {}

    async def get_trade_data(
        self,
        reporter: str,
        partner: str,
        product: str,
        year: int,
        flow: str,
        require_validation: bool = False
    ) -> Optional[TradeDataPoint]:
        """
        Get trade data with automatic fallback.

        Args:
            require_validation: If True, requires 2 sources to agree
        """
        cache_key = f"{reporter}:{partner}:{product}:{year}:{flow}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        results = []

        for source in self.sources:
            try:
                result = await source.get_trade_data(
                    reporter, partner, product, year, flow
                )
                if result:
                    results.append(result)
                    if not require_validation:
                        # Return first valid result
                        self.cache[cache_key] = result
                        return result
            except Exception as e:
                print(f"Source {source.name} failed: {e}")
                continue

        if require_validation and len(results) >= 2:
            # Check if sources agree (within 5% tolerance)
            if self._values_agree(results[0].value_usd, results[1].value_usd):
                self.cache[cache_key] = results[0]
                return results[0]
            else:
                # Return higher priority but flag discrepancy
                result = results[0]
                result.source = f"{result.source} (discrepancy with {results[1].source})"
                return result

        if results:
            self.cache[cache_key] = results[0]
            return results[0]

        return None

    def _values_agree(self, v1: float, v2: float, tolerance: float = 0.05) -> bool:
        """Check if two values are within tolerance."""
        if v1 == 0 and v2 == 0:
            return True
        if v1 == 0 or v2 == 0:
            return False
        diff = abs(v1 - v2) / max(v1, v2)
        return diff <= tolerance

    async def get_comprehensive_data(
        self,
        reporter: str,
        partner: str,
        product: str,
        year: int,
        flow: str
    ) -> Dict[str, TradeDataPoint]:
        """Get data from ALL sources for comparison."""
        results = {}

        tasks = [
            self._fetch_with_name(source, reporter, partner, product, year, flow)
            for source in self.sources
        ]

        completed = await asyncio.gather(*tasks, return_exceptions=True)

        for source, result in zip(self.sources, completed):
            if isinstance(result, TradeDataPoint):
                results[source.name] = result

        return results

    async def _fetch_with_name(
        self,
        source: TradeDataSource,
        reporter: str,
        partner: str,
        product: str,
        year: int,
        flow: str
    ) -> Optional[TradeDataPoint]:
        try:
            return await source.get_trade_data(
                reporter, partner, product, year, flow
            )
        except Exception:
            return None


# Usage Example
async def main():
    sources = [
        ComtradeSource(subscription_key="your-key"),
        WITSSource()
    ]

    aggregator = MultiSourceAggregator(sources)

    # Get US imports from China, electronics (HS 85)
    data = await aggregator.get_trade_data(
        reporter="USA",
        partner="CHN",
        product="85",
        year=2022,
        flow="import"
    )

    if data:
        print(f"Source: {data.source}")
        print(f"Value: ${data.value_usd:,.0f}")

    # Get from all sources for comparison
    all_data = await aggregator.get_comprehensive_data(
        reporter="USA",
        partner="CHN",
        product="85",
        year=2022,
        flow="import"
    )

    for source, point in all_data.items():
        print(f"{source}: ${point.value_usd:,.0f}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Handling Data Discrepancies

When sources disagree, apply these rules:

### Rule 1: Reporter Data Preferred
Generally trust the **reporter's** data over partner's mirror data:
- US reporting imports from China > China reporting exports to US

### Rule 2: More Recent Source Wins
For the same data point:
- Source updated 2024 > Source updated 2023

### Rule 3: Specialized Sources for Domain
- Tariff rates: WITS > Comtrade
- Trade volumes: Comtrade > WITS
- UK-specific: UK Trade Tariff > global sources

### Rule 4: Flag Large Discrepancies
If sources differ by >10%, flag for human review:

```python
def flag_discrepancy(
    value1: float,
    source1: str,
    value2: float,
    source2: str,
    threshold: float = 0.10
) -> Optional[str]:
    if value1 == 0 or value2 == 0:
        return f"Zero value in {source1 if value1 == 0 else source2}"

    diff = abs(value1 - value2) / max(value1, value2)
    if diff > threshold:
        return f"Discrepancy {diff:.1%}: {source1}=${value1:,.0f} vs {source2}=${value2:,.0f}"

    return None
```

---

## Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta
import json
import hashlib

class TradeDataCache:
    """Cache with TTL for trade data."""

    def __init__(self, ttl_hours: int = 24):
        self.cache = {}
        self.ttl = timedelta(hours=ttl_hours)

    def _make_key(self, **kwargs) -> str:
        """Create cache key from query parameters."""
        key_str = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, **kwargs) -> Optional[TradeDataPoint]:
        key = self._make_key(**kwargs)
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.utcnow() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None

    def set(self, data: TradeDataPoint, **kwargs):
        key = self._make_key(**kwargs)
        self.cache[key] = (data, datetime.utcnow())

    def clear_expired(self):
        """Remove expired entries."""
        now = datetime.utcnow()
        expired = [
            k for k, (_, ts) in self.cache.items()
            if now - ts >= self.ttl
        ]
        for k in expired:
            del self.cache[k]
```

---

## Best Practices

1. **Start with highest-priority source** - Don't query all sources by default
2. **Implement fallback** - Gracefully handle source failures
3. **Cache aggressively** - Trade data changes infrequently
4. **Log discrepancies** - Track when sources disagree for data quality
5. **Use async** - Query multiple sources in parallel when needed
6. **Normalize before comparing** - Apply data normalization pattern first
