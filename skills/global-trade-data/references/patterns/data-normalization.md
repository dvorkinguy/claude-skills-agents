# Data Normalization Pattern

Harmonizing trade data from different sources into a consistent format.

## Why Normalize?

Different APIs use different:
- Country codes (ISO2 vs ISO3 vs numeric)
- Product codes (HS revisions, national extensions)
- Value units (USD vs thousands vs local currency)
- Trade flow codes ('M'/'X' vs 'import'/'export' vs 1/2)

---

## Country Code Normalization

### Code Systems in Use

| System | Example (USA) | Used By |
|--------|---------------|---------|
| ISO 3166-1 alpha-2 | US | UK Trade Tariff |
| ISO 3166-1 alpha-3 | USA | WITS, most APIs |
| ISO 3166-1 numeric | 840 | UN Comtrade |
| UN M49 | 840 | UN Statistics |
| Custom | 842 | Comtrade (includes territories) |

### Conversion Implementation

```python
from typing import Dict, Optional
import json

class CountryCodeNormalizer:
    """Convert between country code systems."""

    def __init__(self):
        # Core mappings (extend as needed)
        self.mappings = {
            # ISO2: (ISO3, Numeric, Comtrade)
            'US': ('USA', 840, 842),
            'CN': ('CHN', 156, 156),
            'DE': ('DEU', 276, 276),
            'GB': ('GBR', 826, 826),
            'JP': ('JPN', 392, 392),
            'FR': ('FRA', 250, 251),
            'IT': ('ITA', 380, 381),
            'CA': ('CAN', 124, 124),
            'MX': ('MEX', 484, 484),
            'KR': ('KOR', 410, 410),
            'IN': ('IND', 356, 699),
            'BR': ('BRA', 76, 76),
            'AU': ('AUS', 36, 36),
            'RU': ('RUS', 643, 643),
            # Add more as needed
        }

        # Build reverse lookups
        self._iso3_to_iso2 = {v[0]: k for k, v in self.mappings.items()}
        self._numeric_to_iso2 = {v[1]: k for k, v in self.mappings.items()}
        self._comtrade_to_iso2 = {v[2]: k for k, v in self.mappings.items()}

    def to_iso3(self, code: str) -> Optional[str]:
        """Convert any code to ISO3."""
        code = str(code).upper().strip()

        # Already ISO3
        if code in self._iso3_to_iso2:
            return code

        # From ISO2
        if code in self.mappings:
            return self.mappings[code][0]

        # From numeric
        if code.isdigit():
            num = int(code)
            if num in self._numeric_to_iso2:
                iso2 = self._numeric_to_iso2[num]
                return self.mappings[iso2][0]
            # Try Comtrade codes
            if num in self._comtrade_to_iso2:
                iso2 = self._comtrade_to_iso2[num]
                return self.mappings[iso2][0]

        return None

    def to_iso2(self, code: str) -> Optional[str]:
        """Convert any code to ISO2."""
        code = str(code).upper().strip()

        # Already ISO2
        if code in self.mappings:
            return code

        # From ISO3
        if code in self._iso3_to_iso2:
            return self._iso3_to_iso2[code]

        # From numeric
        if code.isdigit():
            num = int(code)
            if num in self._numeric_to_iso2:
                return self._numeric_to_iso2[num]
            if num in self._comtrade_to_iso2:
                return self._comtrade_to_iso2[num]

        return None

    def to_comtrade(self, code: str) -> Optional[int]:
        """Convert any code to Comtrade numeric."""
        iso2 = self.to_iso2(code)
        if iso2 and iso2 in self.mappings:
            return self.mappings[iso2][2]
        return None

    def normalize(self, code: str, target: str = 'iso3') -> Optional[str]:
        """
        Normalize to target format.

        Args:
            code: Input country code (any format)
            target: 'iso2', 'iso3', 'numeric', or 'comtrade'
        """
        if target == 'iso2':
            return self.to_iso2(code)
        elif target == 'iso3':
            return self.to_iso3(code)
        elif target == 'numeric':
            iso2 = self.to_iso2(code)
            if iso2:
                return str(self.mappings[iso2][1])
        elif target == 'comtrade':
            result = self.to_comtrade(code)
            return str(result) if result else None
        return None


# Usage
normalizer = CountryCodeNormalizer()

# Various inputs all normalize to same output
print(normalizer.to_iso3('US'))     # USA
print(normalizer.to_iso3('USA'))    # USA
print(normalizer.to_iso3('840'))    # USA
print(normalizer.to_iso3('842'))    # USA (Comtrade code)
```

---

## HS Code Normalization

### HS Revision Timeline

| Revision | Year | Changes |
|----------|------|---------|
| HS 1988 (H0) | 1988 | Original |
| HS 1996 (H1) | 1996 | ~400 amendments |
| HS 2002 (H2) | 2002 | ~350 amendments |
| HS 2007 (H3) | 2007 | ~350 amendments |
| HS 2012 (H4) | 2012 | ~220 amendments |
| HS 2017 (H5) | 2017 | ~233 amendments |
| HS 2022 (H6) | 2022 | ~351 amendments |

### Normalization Strategy

```python
from typing import List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class HSCodeMapping:
    """Mapping between HS revisions."""
    source_code: str
    source_revision: str
    target_code: str
    target_revision: str
    mapping_type: str  # 'exact', 'split', 'merge', 'partial'
    weight: float = 1.0  # For splits, proportion allocated

class HSCodeNormalizer:
    """Normalize HS codes across revisions."""

    def __init__(self):
        # Correlation tables (subset - full tables available from UN)
        self.mappings: Dict[Tuple[str, str], List[HSCodeMapping]] = {}
        self._load_correlations()

    def _load_correlations(self):
        """Load HS correlation tables."""
        # Example mappings (real implementation would load from files)
        # HS 2017 to HS 2022 examples
        self._add_mapping('851712', 'H5', '851712', 'H6', 'exact')
        self._add_mapping('854231', 'H5', '854231', 'H6', 'split', 0.6)
        self._add_mapping('854231', 'H5', '854232', 'H6', 'split', 0.4)

    def _add_mapping(
        self,
        source: str,
        source_rev: str,
        target: str,
        target_rev: str,
        map_type: str,
        weight: float = 1.0
    ):
        key = (source, source_rev)
        if key not in self.mappings:
            self.mappings[key] = []
        self.mappings[key].append(HSCodeMapping(
            source_code=source,
            source_revision=source_rev,
            target_code=target,
            target_revision=target_rev,
            mapping_type=map_type,
            weight=weight
        ))

    def normalize_code(
        self,
        code: str,
        source_revision: str,
        target_revision: str = 'H6'
    ) -> List[Tuple[str, float]]:
        """
        Convert HS code between revisions.

        Returns list of (code, weight) tuples for splits.
        """
        # Clean code - remove dots, ensure 6 digits minimum
        code = code.replace('.', '').replace(' ', '')
        if len(code) < 6:
            code = code.ljust(6, '0')

        # Check for direct mapping
        key = (code[:6], source_revision)
        if key in self.mappings:
            mappings = [m for m in self.mappings[key]
                       if m.target_revision == target_revision]
            if mappings:
                return [(m.target_code, m.weight) for m in mappings]

        # No mapping found - return original (may need manual review)
        return [(code, 1.0)]

    def standardize_format(self, code: str, digits: int = 6) -> str:
        """
        Standardize HS code format.

        Args:
            code: Input code (may have dots, spaces)
            digits: Target length (6 for HS, 8/10 for national)
        """
        # Remove formatting
        code = code.replace('.', '').replace(' ', '').replace('-', '')

        # Pad or truncate
        if len(code) < digits:
            code = code.ljust(digits, '0')
        elif len(code) > digits:
            code = code[:digits]

        return code

    def format_display(self, code: str) -> str:
        """Format HS code for display (XXXX.XX.XX)."""
        code = self.standardize_format(code, 6)
        if len(code) >= 4:
            result = code[:4]
            if len(code) >= 6:
                result += '.' + code[4:6]
            if len(code) >= 8:
                result += '.' + code[6:8]
            if len(code) >= 10:
                result += '.' + code[8:10]
            return result
        return code


# Usage
normalizer = HSCodeNormalizer()

# Standardize various inputs
print(normalizer.standardize_format('09.01'))      # 090100
print(normalizer.standardize_format('9012100'))    # 901210
print(normalizer.standardize_format('8471.30.01')) # 847130

# Format for display
print(normalizer.format_display('847130'))  # 8471.30
```

---

## Value Normalization

### Currency and Unit Handling

```python
from decimal import Decimal
from typing import Optional
from datetime import date
import requests

class ValueNormalizer:
    """Normalize trade values to consistent units."""

    # Common unit multipliers
    UNIT_MULTIPLIERS = {
        'units': 1,
        'thousands': 1_000,
        'millions': 1_000_000,
        'billions': 1_000_000_000,
    }

    def __init__(self):
        self._exchange_rates = {}

    def normalize_to_usd(
        self,
        value: float,
        currency: str,
        date_: Optional[date] = None
    ) -> float:
        """
        Convert value to USD.

        Args:
            value: Amount in source currency
            currency: ISO 4217 currency code
            date_: Date for historical rate (optional)
        """
        if currency.upper() == 'USD':
            return value

        rate = self._get_exchange_rate(currency, date_)
        return value * rate

    def normalize_units(
        self,
        value: float,
        source_unit: str,
        target_unit: str = 'units'
    ) -> float:
        """
        Convert between unit scales.

        Common conversions:
        - WITS reports in thousands
        - Some sources use millions
        """
        source_mult = self.UNIT_MULTIPLIERS.get(source_unit.lower(), 1)
        target_mult = self.UNIT_MULTIPLIERS.get(target_unit.lower(), 1)

        return value * source_mult / target_mult

    def _get_exchange_rate(
        self,
        currency: str,
        date_: Optional[date] = None
    ) -> float:
        """Get USD exchange rate (simplified)."""
        # In production, use a proper FX API
        # This is a placeholder with approximate rates
        rates = {
            'EUR': 1.10,
            'GBP': 1.27,
            'JPY': 0.0067,
            'CNY': 0.14,
            'CAD': 0.74,
            'AUD': 0.65,
            'CHF': 1.13,
            'KRW': 0.00075,
            'INR': 0.012,
            'BRL': 0.20,
            'MXN': 0.058,
        }
        return rates.get(currency.upper(), 1.0)


# Usage
normalizer = ValueNormalizer()

# WITS value in thousands EUR -> USD
wits_value = 15234  # 15,234 thousands EUR
usd_value = normalizer.normalize_to_usd(
    normalizer.normalize_units(wits_value, 'thousands'),
    'EUR'
)
print(f"${usd_value:,.0f}")  # $16,757,400
```

---

## Trade Flow Normalization

### Flow Code Mappings

| Source | Import | Export | Re-export |
|--------|--------|--------|-----------|
| UN Comtrade | M | X | - |
| WITS | MPRT | XPRT | - |
| UK API | import | export | - |
| Custom | 1 | 2 | 3 |

```python
from enum import Enum

class TradeFlow(Enum):
    IMPORT = 'import'
    EXPORT = 'export'
    RE_EXPORT = 're-export'
    RE_IMPORT = 're-import'

class FlowNormalizer:
    """Normalize trade flow codes."""

    FLOW_MAPPINGS = {
        # Imports
        'M': TradeFlow.IMPORT,
        'm': TradeFlow.IMPORT,
        'MPRT': TradeFlow.IMPORT,
        'import': TradeFlow.IMPORT,
        'imports': TradeFlow.IMPORT,
        '1': TradeFlow.IMPORT,
        1: TradeFlow.IMPORT,

        # Exports
        'X': TradeFlow.EXPORT,
        'x': TradeFlow.EXPORT,
        'XPRT': TradeFlow.EXPORT,
        'export': TradeFlow.EXPORT,
        'exports': TradeFlow.EXPORT,
        '2': TradeFlow.EXPORT,
        2: TradeFlow.EXPORT,

        # Re-exports
        'RX': TradeFlow.RE_EXPORT,
        're-export': TradeFlow.RE_EXPORT,
        'reexport': TradeFlow.RE_EXPORT,
        '3': TradeFlow.RE_EXPORT,
        3: TradeFlow.RE_EXPORT,
    }

    @classmethod
    def normalize(cls, flow_code) -> TradeFlow:
        """Convert any flow code to standard enum."""
        if isinstance(flow_code, TradeFlow):
            return flow_code

        normalized = cls.FLOW_MAPPINGS.get(flow_code)
        if normalized:
            return normalized

        # Try string conversion
        if isinstance(flow_code, str):
            normalized = cls.FLOW_MAPPINGS.get(flow_code.lower())
            if normalized:
                return normalized

        raise ValueError(f"Unknown flow code: {flow_code}")

    @classmethod
    def to_comtrade(cls, flow: TradeFlow) -> str:
        """Convert to Comtrade format."""
        mapping = {
            TradeFlow.IMPORT: 'M',
            TradeFlow.EXPORT: 'X',
            TradeFlow.RE_EXPORT: 'RX',
            TradeFlow.RE_IMPORT: 'RM',
        }
        return mapping[flow]

    @classmethod
    def to_wits(cls, flow: TradeFlow) -> str:
        """Convert to WITS format."""
        mapping = {
            TradeFlow.IMPORT: 'MPRT-TRD-VL',
            TradeFlow.EXPORT: 'XPRT-TRD-VL',
        }
        return mapping.get(flow)


# Usage
normalizer = FlowNormalizer()

print(normalizer.normalize('M'))        # TradeFlow.IMPORT
print(normalizer.normalize('exports'))  # TradeFlow.EXPORT
print(normalizer.normalize(1))          # TradeFlow.IMPORT

print(normalizer.to_comtrade(TradeFlow.EXPORT))  # X
```

---

## Complete Normalization Pipeline

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class NormalizedTradeRecord:
    """Fully normalized trade record."""
    reporter_iso3: str
    partner_iso3: str
    hs_code: str  # 6-digit, HS 2022
    year: int
    flow: TradeFlow
    value_usd: float
    quantity: Optional[float] = None
    quantity_unit: Optional[str] = None
    source: str = ""
    original_reporter: str = ""
    original_partner: str = ""
    original_product: str = ""
    original_value: float = 0.0

class TradeDataNormalizer:
    """Complete normalization pipeline."""

    def __init__(self):
        self.country_normalizer = CountryCodeNormalizer()
        self.hs_normalizer = HSCodeNormalizer()
        self.value_normalizer = ValueNormalizer()
        self.flow_normalizer = FlowNormalizer()

    def normalize(
        self,
        reporter: str,
        partner: str,
        product: str,
        year: int,
        flow,
        value: float,
        currency: str = 'USD',
        value_unit: str = 'units',
        hs_revision: str = 'H6',
        quantity: Optional[float] = None,
        quantity_unit: Optional[str] = None,
        source: str = ""
    ) -> NormalizedTradeRecord:
        """
        Normalize a trade record from any source.
        """
        # Normalize countries
        reporter_iso3 = self.country_normalizer.to_iso3(reporter)
        partner_iso3 = self.country_normalizer.to_iso3(partner)

        if not reporter_iso3:
            raise ValueError(f"Unknown reporter: {reporter}")
        if not partner_iso3:
            raise ValueError(f"Unknown partner: {partner}")

        # Normalize HS code
        hs_mappings = self.hs_normalizer.normalize_code(
            product, hs_revision, 'H6'
        )
        # Take primary mapping (for splits, may need special handling)
        hs_code = hs_mappings[0][0]

        # Normalize flow
        flow_enum = self.flow_normalizer.normalize(flow)

        # Normalize value
        value_units = self.value_normalizer.normalize_units(
            value, value_unit, 'units'
        )
        value_usd = self.value_normalizer.normalize_to_usd(
            value_units, currency
        )

        return NormalizedTradeRecord(
            reporter_iso3=reporter_iso3,
            partner_iso3=partner_iso3,
            hs_code=hs_code,
            year=year,
            flow=flow_enum,
            value_usd=value_usd,
            quantity=quantity,
            quantity_unit=quantity_unit,
            source=source,
            original_reporter=reporter,
            original_partner=partner,
            original_product=product,
            original_value=value
        )


# Usage
pipeline = TradeDataNormalizer()

# WITS record (thousands EUR, ISO3 codes)
record = pipeline.normalize(
    reporter='DEU',
    partner='USA',
    product='8471',
    year=2022,
    flow='XPRT',
    value=1500000,  # 1.5 million thousands = 1.5 billion EUR
    currency='EUR',
    value_unit='thousands',
    source='wits'
)

print(f"{record.reporter_iso3} -> {record.partner_iso3}")
print(f"HS: {record.hs_code}")
print(f"Flow: {record.flow.value}")
print(f"Value: ${record.value_usd:,.0f}")
```

---

## Best Practices

1. **Normalize early** - Convert data immediately after retrieval
2. **Keep originals** - Store original values for debugging
3. **Use enums** - Prevent string comparison errors
4. **Validate** - Check normalized values are reasonable
5. **Log conversions** - Track what was normalized for audit
6. **Update mappings** - Keep country/HS tables current
