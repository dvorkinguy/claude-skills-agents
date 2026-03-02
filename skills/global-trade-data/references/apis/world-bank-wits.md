# World Bank WITS API

World Integrated Trade Solution - Trade statistics, tariff, and non-tariff data.

## Quick Reference

| Property | Value |
|----------|-------|
| **Base URL** | `https://wits.worldbank.org/API/V1` |
| **Auth** | None required (public API) |
| **Format** | XML (default), JSON available |
| **Rate Limit** | Not documented (be respectful) |
| **Coverage** | 1988-present, 200+ countries |

## API Structure (SDMX-Based)

The WITS API follows SDMX (Statistical Data and Metadata eXchange) conventions.

### URL Pattern
```
https://wits.worldbank.org/API/V1/{datatype}/country/{country}/product/{product}/year/{year}
```

### Response Format
Add `?format=JSON` for JSON response (default is XML).

---

## Data Types Available

### 1. UNCTAD TRAINS (Tariff Data)

Trade Analysis Information System - detailed tariff rates.

**Endpoint Pattern:**
```
/V1/SDMX/V21/datasource/tradestats-tariff/reporter/{reporter}/year/{year}/partner/{partner}/product/{product}
```

**Available Indicators:**
- `AHS` - Applied MFN tariff rates
- `BND` - Bound tariff rates
- `PRF` - Preferential tariff rates

**Example - Get US tariffs on automobiles (HS 8703):**
```
https://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-tariff/reporter/usa/year/2022/partner/all/product/8703?format=JSON
```

### 2. Trade Statistics

Import/export values and quantities.

**Endpoint Pattern:**
```
/V1/SDMX/V21/datasource/tradestats-trade/reporter/{reporter}/year/{year}/partner/{partner}/product/{product}/indicator/{indicator}
```

**Indicators:**
- `XPRT-TRD-VL` - Export trade value (USD thousands)
- `MPRT-TRD-VL` - Import trade value (USD thousands)
- `XPRT-TRD-QTY` - Export quantity
- `MPRT-TRD-QTY` - Import quantity

**Example - Get China exports to USA:**
```
https://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-trade/reporter/chn/year/2022/partner/usa/product/all/indicator/XPRT-TRD-VL?format=JSON
```

### 3. Development Indicators

Macroeconomic context for trade analysis.

**Endpoint:**
```
/V1/SDMX/V21/datasource/WDI/country/{country}/indicator/{indicator}/year/{year}
```

**Key Indicators:**
- `NY.GDP.MKTP.CD` - GDP (current USD)
- `NE.TRD.GNFS.ZS` - Trade (% of GDP)
- `BX.GSR.GNFS.CD` - Exports of goods and services
- `BM.GSR.GNFS.CD` - Imports of goods and services

---

## Country Codes

WITS uses ISO3 country codes (3-letter).

**Common codes:**
| Code | Country |
|------|---------|
| USA | United States |
| CHN | China |
| DEU | Germany |
| JPN | Japan |
| GBR | United Kingdom |
| FRA | France |
| IND | India |
| BRA | Brazil |
| ALL | All countries |
| WLD | World aggregate |

**Get all country codes:**
```
https://wits.worldbank.org/API/V1/wits/datasource/tradestats-trade/country/ALL
```

---

## Product Classifications

### HS Nomenclature Revisions
- `H0` - HS 1988/92
- `H1` - HS 1996
- `H2` - HS 2002
- `H3` - HS 2007
- `H4` - HS 2012
- `H5` - HS 2017
- `H6` - HS 2022

### SITC (Standard International Trade Classification)
- `S1` - SITC Rev 1
- `S2` - SITC Rev 2
- `S3` - SITC Rev 3
- `S4` - SITC Rev 4

**Get product hierarchy:**
```
https://wits.worldbank.org/API/V1/wits/datasource/tradestats-trade/dataavailability/reporter/USA/partner/ALL/year/2022/tradeflow/XPRT/productcode/ALL/product/HS
```

---

## Python Integration

### Using requests Library

```python
import requests
import pandas as pd

class WITSClient:
    BASE_URL = "https://wits.worldbank.org/API/V1"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json'
        })

    def get_tariff_data(
        self,
        reporter: str,
        year: int,
        partner: str = "all",
        product: str = "all"
    ) -> dict:
        """Get tariff rates from UNCTAD TRAINS."""
        url = (
            f"{self.BASE_URL}/SDMX/V21/datasource/tradestats-tariff"
            f"/reporter/{reporter}/year/{year}"
            f"/partner/{partner}/product/{product}"
        )
        response = self.session.get(url, params={"format": "JSON"})
        response.raise_for_status()
        return response.json()

    def get_trade_data(
        self,
        reporter: str,
        year: int,
        partner: str = "all",
        product: str = "all",
        indicator: str = "XPRT-TRD-VL"
    ) -> dict:
        """Get trade statistics (imports/exports)."""
        url = (
            f"{self.BASE_URL}/SDMX/V21/datasource/tradestats-trade"
            f"/reporter/{reporter}/year/{year}"
            f"/partner/{partner}/product/{product}"
            f"/indicator/{indicator}"
        )
        response = self.session.get(url, params={"format": "JSON"})
        response.raise_for_status()
        return response.json()

    def get_countries(self) -> dict:
        """Get list of available countries."""
        url = f"{self.BASE_URL}/wits/datasource/tradestats-trade/country/ALL"
        response = self.session.get(url, params={"format": "JSON"})
        response.raise_for_status()
        return response.json()


# Usage
client = WITSClient()

# Get US tariffs on Chinese goods
tariffs = client.get_tariff_data(
    reporter="usa",
    year=2022,
    partner="chn"
)

# Get German exports
exports = client.get_trade_data(
    reporter="deu",
    year=2022,
    indicator="XPRT-TRD-VL"
)
```

### Parsing SDMX Response

```python
def parse_sdmx_response(response: dict) -> pd.DataFrame:
    """Parse WITS SDMX JSON response to DataFrame."""

    # SDMX structure varies - this handles common patterns
    if "dataSets" in response:
        datasets = response["dataSets"]
        if datasets and "observations" in datasets[0]:
            obs = datasets[0]["observations"]

            # Build records from observations
            records = []
            for key, values in obs.items():
                indices = key.split(":")
                records.append({
                    "dimension_indices": indices,
                    "value": values[0] if values else None
                })

            return pd.DataFrame(records)

    return pd.DataFrame()
```

---

## Data Availability Queries

Check what data exists before querying:

### Available Years
```
https://wits.worldbank.org/API/V1/wits/datasource/tradestats-trade/dataavailability/reporter/USA/year/ALL
```

### Available Partners
```
https://wits.worldbank.org/API/V1/wits/datasource/tradestats-trade/dataavailability/reporter/USA/year/2022/partner/ALL
```

### Available Products
```
https://wits.worldbank.org/API/V1/wits/datasource/tradestats-trade/dataavailability/reporter/USA/year/2022/productcode/ALL
```

---

## Key Differences from UN Comtrade

| Aspect | WITS | UN Comtrade |
|--------|------|-------------|
| **Tariff data** | ✅ Comprehensive | ❌ Not available |
| **NTM data** | ✅ Available | ❌ Not available |
| **Trade data** | ✅ Via TRAINS | ✅ Primary source |
| **API auth** | None required | Subscription key |
| **Python library** | Manual requests | `comtradeapicall` |
| **Response format** | SDMX (complex) | Simple JSON |
| **Rate limiting** | Undocumented | Documented |

## Best Practices

1. **Use for tariff queries** - WITS is the primary source for tariff data
2. **Check availability first** - Query data availability before large requests
3. **Cache responses** - API can be slow; cache results locally
4. **Handle SDMX parsing** - Response format requires custom parsing
5. **Combine with Comtrade** - Use WITS for tariffs, Comtrade for trade volumes

---

## Related Resources

- [WITS Portal](https://wits.worldbank.org/)
- [UNCTAD TRAINS](https://trainsonline.unctad.org/)
- [SDMX Documentation](https://sdmx.org/)
