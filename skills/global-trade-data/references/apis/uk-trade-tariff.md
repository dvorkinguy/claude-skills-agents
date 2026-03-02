# UK Trade Tariff API

UK Government's official API for commodity codes, duty rates, and import/export regulations.

## Quick Reference

| Property | Value |
|----------|-------|
| **Base URL** | `https://www.trade-tariff.service.gov.uk/api/v2` |
| **Auth** | None required (public API) |
| **Format** | JSON:API specification |
| **Rate Limit** | Not published (be respectful) |
| **Coverage** | UK-specific tariffs, post-Brexit |

## Key Endpoints

### 1. Commodity Lookup

Get details for a specific commodity code.

**Endpoint:**
```
GET /commodities/{commodity_code}
```

**Example - Get info on coffee (0901):**
```
https://www.trade-tariff.service.gov.uk/api/v2/commodities/0901210000
```

**Response includes:**
- Duty rates (MFN, preferential)
- VAT rates
- Measures (quotas, licenses, restrictions)
- Legal requirements
- Additional codes

### 2. Headings

Get all commodities under an HS heading.

**Endpoint:**
```
GET /headings/{heading_code}
```

**Example - All coffee products (heading 09.01):**
```
https://www.trade-tariff.service.gov.uk/api/v2/headings/0901
```

### 3. Chapters

Get all headings in a chapter.

**Endpoint:**
```
GET /chapters/{chapter_code}
```

**Example - Live animals (chapter 01):**
```
https://www.trade-tariff.service.gov.uk/api/v2/chapters/01
```

### 4. Sections

Get overview of tariff sections.

**Endpoint:**
```
GET /sections
GET /sections/{section_id}
```

### 5. Search

Search for commodities by keyword.

**Endpoint:**
```
GET /search?q={query}
```

**Example - Search for "bicycle":**
```
https://www.trade-tariff.service.gov.uk/api/v2/search?q=bicycle
```

### 6. Geographical Areas

Get country/region codes for preferential rates.

**Endpoint:**
```
GET /geographical_areas
GET /geographical_areas/{id}
```

---

## Understanding UK Commodity Codes

UK uses 10-digit commodity codes:

```
0901 21 00 00
│    │  │  └── UK-specific (digits 9-10)
│    │  └───── Subheading (digits 7-8)
│    └──────── HS Subheading (digits 5-6)
└───────────── HS Chapter/Heading (digits 1-4)
```

**Structure:**
- Digits 1-6: International HS code
- Digits 7-8: Combined Nomenclature (EU origin)
- Digits 9-10: UK TARIC (UK-specific)

---

## Python Integration

```python
import requests
from typing import Optional

class UKTradeTariffClient:
    BASE_URL = "https://www.trade-tariff.service.gov.uk/api/v2"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json'
        })

    def get_commodity(self, code: str) -> dict:
        """Get commodity details by 10-digit code."""
        # Pad code to 10 digits if needed
        code = code.ljust(10, '0')
        response = self.session.get(f"{self.BASE_URL}/commodities/{code}")
        response.raise_for_status()
        return response.json()

    def get_heading(self, code: str) -> dict:
        """Get all commodities under a 4-digit heading."""
        code = code[:4]
        response = self.session.get(f"{self.BASE_URL}/headings/{code}")
        response.raise_for_status()
        return response.json()

    def get_chapter(self, code: str) -> dict:
        """Get chapter overview (2-digit)."""
        code = code[:2].zfill(2)
        response = self.session.get(f"{self.BASE_URL}/chapters/{code}")
        response.raise_for_status()
        return response.json()

    def search(self, query: str) -> dict:
        """Search commodities by keyword."""
        response = self.session.get(
            f"{self.BASE_URL}/search",
            params={"q": query}
        )
        response.raise_for_status()
        return response.json()

    def get_duty_rate(self, code: str) -> dict:
        """Extract duty information from commodity data."""
        data = self.get_commodity(code)

        # Parse JSON:API response
        measures = []
        if 'included' in data:
            for item in data['included']:
                if item['type'] == 'measure':
                    measures.append({
                        'id': item['id'],
                        'type': item.get('attributes', {}).get('measure_type_description'),
                        'duty': item.get('attributes', {}).get('duty_expression', {})
                    })

        return {
            'commodity_code': code,
            'measures': measures
        }


# Usage
client = UKTradeTariffClient()

# Look up wine (2204)
wine = client.get_heading("2204")
print(f"Found {len(wine.get('data', {}).get('relationships', {}).get('commodities', {}).get('data', []))} commodities")

# Search for specific product
results = client.search("electric bicycle")

# Get duty rates
duties = client.get_duty_rate("8711600010")  # Electric motorcycles
```

---

## Duty Rate Structure

The API returns duty rates in JSON:API format with nested relationships.

### Measure Types
| Code | Description |
|------|-------------|
| 103 | Third country duty (MFN rate) |
| 105 | Preferential duty |
| 112 | Autonomous tariff suspension |
| 115 | Autonomous duty reduction |
| 142 | Tariff quota |
| 143 | Inward processing |

### Duty Expression Format
```json
{
  "duty_expression": {
    "base": "8.00 %",
    "formatted_base": "8.00%",
    "verbose_duty": "8.00%"
  }
}
```

---

## Post-Brexit Considerations

**UK Global Tariff (UKGT):**
- Replaced EU Common External Tariff January 2021
- Simplified rate structure
- Some rates lower than EU equivalents

**Trade Agreements:**
- UK-EU Trade and Cooperation Agreement
- Rollover FTAs with 70+ countries
- New FTAs (Australia, New Zealand, CPTPP)

**Country of Origin:**
- Rules of origin determine preferential eligibility
- Cumulation provisions with partner countries

---

## Related Resources

- [UK Trade Tariff Portal](https://www.trade-tariff.service.gov.uk/)
- [Check duties and customs](https://www.gov.uk/check-duties-customs-exporting)
- [Trade Tariff Tool](https://www.gov.uk/trade-tariff)
- [API Documentation](https://www.trade-tariff.service.gov.uk/howto)
