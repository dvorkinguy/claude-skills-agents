# Global Trade Alert API

Policy intervention monitoring database - tracking trade-affecting government measures worldwide.

## Quick Reference

| Property | Value |
|----------|-------|
| **Website** | [globaltradealert.org](https://www.globaltradealert.org/) |
| **Coverage** | 70,000+ interventions since 2009 |
| **Jurisdictions** | 50+ countries monitored |
| **Updates** | Weekly (average 70 new entries) |
| **Data Access** | Bulk downloads, limited API |

## Data Coverage

### Intervention Types Tracked

**Trade Remedies:**
- Anti-dumping duties
- Countervailing duties
- Safeguard measures

**Tariff Measures:**
- MFN tariff increases
- Tariff reductions
- Tariff-rate quotas

**Non-Tariff Measures:**
- Import licensing
- Export restrictions
- Quantitative restrictions
- Technical barriers (TBT)
- Sanitary measures (SPS)

**Subsidies:**
- Export subsidies
- Production subsidies
- State aid
- Tax incentives

**Other:**
- Public procurement restrictions
- Investment measures
- Migration policies affecting trade
- Intellectual property measures

---

## Data Access Methods

### 1. Bulk Data Downloads

**Available Formats:**
- Excel spreadsheets
- CSV files
- Machine-readable datasets

**Download Portal:**
```
https://www.globaltradealert.org/data_extraction
```

### 2. GTA REST API

Limited programmatic access available for researchers.

**Base URL:**
```
https://www.globaltradealert.org/api/v1
```

**Note:** API access may require registration/approval for full access.

### 3. Data Fields

Each intervention record includes:

| Field | Description |
|-------|-------------|
| `intervention_id` | Unique identifier |
| `title` | Brief description |
| `implementing_jurisdiction` | Country taking action |
| `affected_jurisdictions` | Countries impacted |
| `products_affected` | HS codes or sectors |
| `announcement_date` | When announced |
| `implementation_date` | When took effect |
| `removal_date` | If temporary, when ended |
| `assessment` | Red (harmful), Amber (may be harmful), Green (liberalizing) |
| `source_url` | Official source document |

---

## Classification System

### Color Coding

**🔴 Red (Harmful):**
- Almost certainly discriminates against foreign commercial interests
- Examples: tariff increases, import bans, subsidies to domestic competitors

**🟡 Amber (Likely Harmful):**
- Likely discriminates but less certain
- Examples: opaque regulations, potentially discriminatory standards

**🟢 Green (Liberalizing):**
- Benefits foreign commercial interests
- Examples: tariff cuts, removing quotas, opening procurement

### Sectors Covered

GTA tracks interventions across all sectors using:
- HS codes (product-level)
- CPC codes (services)
- Sector aggregations (e.g., "steel", "automotive", "pharmaceuticals")

---

## Python Integration

```python
import requests
import pandas as pd
from typing import Optional, List

class GTAClient:
    """Client for Global Trade Alert data access."""

    BASE_URL = "https://www.globaltradealert.org"

    def __init__(self, api_key: Optional[str] = None):
        self.session = requests.Session()
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'

    def search_interventions(
        self,
        implementing_jurisdiction: Optional[str] = None,
        affected_jurisdiction: Optional[str] = None,
        hs_codes: Optional[List[str]] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        assessment: Optional[str] = None  # 'red', 'amber', 'green'
    ) -> pd.DataFrame:
        """
        Search GTA database for interventions.

        Note: This is a simplified interface. Actual API endpoints
        may vary - check GTA documentation for current access.
        """
        params = {}

        if implementing_jurisdiction:
            params['implementing'] = implementing_jurisdiction
        if affected_jurisdiction:
            params['affected'] = affected_jurisdiction
        if hs_codes:
            params['products'] = ','.join(hs_codes)
        if year_from:
            params['year_from'] = year_from
        if year_to:
            params['year_to'] = year_to
        if assessment:
            params['assessment'] = assessment

        # Example endpoint - verify with GTA docs
        response = self.session.get(
            f"{self.BASE_URL}/api/v1/interventions",
            params=params
        )

        if response.status_code == 200:
            return pd.DataFrame(response.json().get('data', []))
        else:
            raise Exception(f"API error: {response.status_code}")

    def get_intervention_detail(self, intervention_id: int) -> dict:
        """Get full details of a specific intervention."""
        response = self.session.get(
            f"{self.BASE_URL}/api/v1/intervention/{intervention_id}"
        )
        response.raise_for_status()
        return response.json()


def load_gta_bulk_data(filepath: str) -> pd.DataFrame:
    """
    Load GTA bulk download file.

    Download from: https://www.globaltradealert.org/data_extraction
    """
    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    elif filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        raise ValueError("Unsupported format. Use .xlsx or .csv")

    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    return df


# Example: Analyze trade war interventions
def analyze_us_china_measures(df: pd.DataFrame) -> dict:
    """Analyze US-China trade interventions from GTA data."""

    # Filter for US implementing, China affected (and vice versa)
    us_on_china = df[
        (df['implementing_jurisdiction'] == 'United States') &
        (df['affected_jurisdictions'].str.contains('China', na=False))
    ]

    china_on_us = df[
        (df['implementing_jurisdiction'] == 'China') &
        (df['affected_jurisdictions'].str.contains('United States', na=False))
    ]

    return {
        'us_measures_against_china': len(us_on_china),
        'china_measures_against_us': len(china_on_us),
        'us_harmful': len(us_on_china[us_on_china['assessment'] == 'Red']),
        'china_harmful': len(china_on_us[china_on_us['assessment'] == 'Red']),
    }
```

---

## Use Cases

### 1. Trade War Tracking
Monitor escalation/de-escalation of trade tensions between major economies.

### 2. Supply Chain Risk
Identify policy changes affecting specific product categories.

### 3. Market Access Analysis
Track barriers in target export markets.

### 4. Regulatory Intelligence
Early warning of upcoming trade restrictions.

### 5. Academic Research
Quantitative analysis of protectionism trends.

---

## Combining with Other Sources

**GTA + UN Comtrade:**
- GTA identifies WHEN restrictions were imposed
- Comtrade shows trade VOLUME impact before/after

**GTA + WITS:**
- GTA for policy announcements
- WITS for actual tariff rate changes

**Example workflow:**
1. GTA: Find Section 301 tariff announcement (2018)
2. Comtrade: Query US-China trade flows 2017-2020
3. Calculate trade diversion effects

---

## Related Resources

- [GTA Data Portal](https://www.globaltradealert.org/data_extraction)
- [GTA Reports](https://www.globaltradealert.org/reports)
- [St. Gallen Endowment](https://www.globaltradealert.org/about) (Host institution)
- [GTA Methodology](https://www.globaltradealert.org/about#methodology)
