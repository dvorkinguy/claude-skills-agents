# US Tariffs API (tariffsapi.com)

Commercial API for US HTS code lookups and real-time tariff rates.

## Quick Reference

| Property | Value |
|----------|-------|
| **Website** | [tariffsapi.com](https://tariffsapi.com) |
| **Coverage** | US Harmonized Tariff Schedule |
| **Updates** | Real-time with USITC changes |
| **Auth** | API key required |
| **Pricing** | Free tier available, paid plans |

## Key Features

- **HTS Code Lookups:** Search and validate US commodity codes
- **Duty Rates:** Current MFN and preferential rates
- **Section 301 Duties:** China-specific additional tariffs
- **Country of Origin:** Rules for preferential treatment
- **Rate History:** Historical rate changes

---

## API Endpoints

### 1. HTS Code Lookup

Get tariff information for a specific HTS code.

**Endpoint:**
```
GET /api/v1/hts/{hts_code}
```

**Parameters:**
- `hts_code` - 8 or 10 digit HTS code

**Response includes:**
- Description
- General duty rate (MFN)
- Special duty rates (FTAs)
- Section 301 additional duties
- Unit of quantity

### 2. Search by Description

Find HTS codes by product description.

**Endpoint:**
```
GET /api/v1/search?q={query}
```

**Parameters:**
- `q` - Search terms
- `limit` - Results per page (default 25)

### 3. Section 301 Duties

Get China-specific tariff information.

**Endpoint:**
```
GET /api/v1/section301/{hts_code}
```

**Response:**
- List number (1, 2, 3, 4A, 4B)
- Additional duty rate (7.5% or 25%)
- Exclusions if applicable
- Effective dates

### 4. FTA Rates

Get preferential rates under trade agreements.

**Endpoint:**
```
GET /api/v1/fta/{hts_code}/{country_code}
```

**Supported Agreements:**
- USMCA (Mexico, Canada)
- KORUS (South Korea)
- CAFTA-DR (Central America)
- Australia FTA
- Singapore FTA
- And others

---

## Understanding US Tariff Structure

### HTS Code Format (10 digits)

```
8471.30.01.00
│    │  │  └── Statistical suffix (digits 9-10)
│    │  └───── US subheading (digits 7-8)
│    └──────── HS subheading (digits 5-6)
└───────────── HS heading (digits 1-4)
```

### Duty Rate Types

**Column 1 General (MFN):**
- Applies to most countries
- WTO Most Favored Nation rate

**Column 1 Special:**
- Preferential rates under FTAs
- GSP rates for developing countries
- Format: `Free (A,AU,BH,CA,CL,CO,...)`

**Column 2:**
- Rarely used
- Applies to Cuba, North Korea

### Section 301 (China Tariffs)

Additional duties on Chinese goods:
| List | Additional Duty | Products |
|------|-----------------|----------|
| 1 | 25% | ~$34B industrial goods |
| 2 | 25% | ~$16B machinery, electronics |
| 3 | 25% | ~$200B various goods |
| 4A | 7.5% | ~$120B consumer goods |
| 4B | Suspended | Various |

---

## Python Integration

```python
import requests
from typing import Optional, Dict, List

class TariffsAPIClient:
    """Client for tariffsapi.com US tariff lookups."""

    BASE_URL = "https://api.tariffsapi.com/api/v1"

    def __init__(self, api_key: str):
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        })

    def get_hts(self, hts_code: str) -> Dict:
        """
        Get tariff data for an HTS code.

        Args:
            hts_code: 8 or 10 digit HTS code (dots optional)

        Returns:
            Dict with duty rates and product info
        """
        # Remove dots and spaces
        code = hts_code.replace('.', '').replace(' ', '')

        response = self.session.get(f"{self.BASE_URL}/hts/{code}")
        response.raise_for_status()
        return response.json()

    def search(self, query: str, limit: int = 25) -> List[Dict]:
        """
        Search HTS codes by description.

        Args:
            query: Search terms
            limit: Max results

        Returns:
            List of matching HTS codes
        """
        response = self.session.get(
            f"{self.BASE_URL}/search",
            params={'q': query, 'limit': limit}
        )
        response.raise_for_status()
        return response.json().get('results', [])

    def get_section_301(self, hts_code: str) -> Optional[Dict]:
        """
        Check if product has Section 301 duties.

        Args:
            hts_code: 8 or 10 digit HTS code

        Returns:
            Section 301 info or None if not applicable
        """
        code = hts_code.replace('.', '').replace(' ', '')

        response = self.session.get(f"{self.BASE_URL}/section301/{code}")

        if response.status_code == 404:
            return None  # No 301 duties

        response.raise_for_status()
        return response.json()

    def get_fta_rate(self, hts_code: str, country: str) -> Optional[Dict]:
        """
        Get FTA preferential rate for a country.

        Args:
            hts_code: 8 or 10 digit HTS code
            country: ISO2 country code (e.g., 'MX', 'CA', 'KR')

        Returns:
            FTA rate info or None if no preference
        """
        code = hts_code.replace('.', '').replace(' ', '')

        response = self.session.get(
            f"{self.BASE_URL}/fta/{code}/{country}"
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()

    def calculate_total_duty(
        self,
        hts_code: str,
        country_of_origin: str,
        value_usd: float
    ) -> Dict:
        """
        Calculate total applicable duty.

        Args:
            hts_code: Product HTS code
            country_of_origin: ISO2 code
            value_usd: Customs value in USD

        Returns:
            Breakdown of applicable duties
        """
        hts_data = self.get_hts(hts_code)
        s301_data = self.get_section_301(hts_code)
        fta_data = self.get_fta_rate(hts_code, country_of_origin)

        # Parse duty rate (simplified - real logic more complex)
        base_rate = hts_data.get('general_rate', '0%')
        base_pct = self._parse_rate(base_rate)

        # Check for FTA preference
        if fta_data:
            base_pct = self._parse_rate(fta_data.get('rate', base_rate))

        # Add Section 301 if from China
        s301_pct = 0.0
        if country_of_origin == 'CN' and s301_data:
            s301_pct = self._parse_rate(s301_data.get('additional_duty', '0%'))

        total_pct = base_pct + s301_pct
        duty_amount = value_usd * (total_pct / 100)

        return {
            'hts_code': hts_code,
            'country': country_of_origin,
            'value_usd': value_usd,
            'base_rate': f"{base_pct}%",
            'section_301_rate': f"{s301_pct}%" if s301_pct else None,
            'total_rate': f"{total_pct}%",
            'duty_amount': round(duty_amount, 2)
        }

    def _parse_rate(self, rate_str: str) -> float:
        """Parse percentage from rate string."""
        if 'Free' in rate_str:
            return 0.0

        import re
        match = re.search(r'(\d+\.?\d*)\s*%', rate_str)
        if match:
            return float(match.group(1))
        return 0.0


# Usage
client = TariffsAPIClient(api_key="your-api-key")

# Look up laptop computers
laptop = client.get_hts("8471.30.01.00")
print(f"Description: {laptop.get('description')}")
print(f"MFN Rate: {laptop.get('general_rate')}")

# Check Section 301
s301 = client.get_section_301("8471.30.01.00")
if s301:
    print(f"Section 301: +{s301.get('additional_duty')}")

# Calculate landed cost
duty = client.calculate_total_duty(
    hts_code="8471.30.01.00",
    country_of_origin="CN",
    value_usd=500.00
)
print(f"Total duty on $500 laptop from China: ${duty['duty_amount']}")
```

---

## Alternative: Free USITC Data

For budget-constrained projects, use official USITC sources:

**HTS Online:**
```
https://hts.usitc.gov/
```

**DataWeb (Trade Statistics):**
```
https://dataweb.usitc.gov/
```

**Tariff Database:**
```
https://www.usitc.gov/tariff_affairs
```

---

## Related Resources

- [USITC HTS Search](https://hts.usitc.gov/)
- [CBP Rulings](https://rulings.cbp.gov/)
- [Section 301 USTR Page](https://ustr.gov/issue-areas/enforcement/section-301-investigations)
- [USMCA Text](https://ustr.gov/trade-agreements/free-trade-agreements/united-states-mexico-canada-agreement)
