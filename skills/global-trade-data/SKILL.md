---
name: global-trade-data
description: Build applications with global trade data. Use when working with trade statistics, tariffs, HS codes, imports/exports, customs data, or integrating trade APIs (UN Comtrade, World Bank WITS, UK Trade Tariff, Global Trade Alert, US Tariffs API). Includes domain knowledge and API references.
---

# Global Trade Data

Build applications that consume and analyze international trade data.

## Quick Reference

### HS Code Structure
```
01          Chapter (2-digit) - Live animals
0101        Heading (4-digit) - Horses, asses, mules
010110      Subheading (6-digit) - Pure-bred breeding horses
01011010    National (8-10 digit) - Country-specific
```

### Key Country Codes
| Country | Comtrade | ISO3 | ISO2 |
|---------|----------|------|------|
| Israel | 376 | ISR | IL |
| USA | 842 | USA | US |
| China | 156 | CHN | CN |
| Germany | 276 | DEU | DE |
| World | 0 | WLD | - |

### Trade Flow Codes
| Code | Description |
|------|-------------|
| M | Imports |
| X | Exports |
| RM | Re-imports |
| RX | Re-exports |

### Tariff Types
| Type | Example | Description |
|------|---------|-------------|
| Ad valorem | 5% | Percentage of value |
| Specific | $2/kg | Fixed per unit |
| Compound | 5% + $2/kg | Combined |
| AVE | 7.5% | Ad valorem equivalent |

### Trade Terminology
| Term | Description |
|------|-------------|
| **FOB** | Free on Board - export value (excludes shipping) |
| **CIF** | Cost, Insurance, Freight - import value (includes shipping) |
| **MFN** | Most Favored Nation - default tariff rate |
| **Preferential** | Reduced rate under trade agreement |
| **Bound rate** | WTO maximum tariff ceiling |
| **Applied rate** | Actual rate charged |
| **Mirror data** | Partner's reported trade (for validation) |

## Available Trade APIs

### UN Comtrade (Primary)
- **Data**: International merchandise trade statistics
- **Coverage**: 200+ countries, 1962-present
- **Library**: `comtradeapicall` (Python)
- **Auth**: Subscription key for full access
- See: `references/apis/un-comtrade.md`

### World Bank WITS
- **Data**: Tariffs (UNCTAD TRAINS), trade stats, development indicators
- **Coverage**: Global, 1988-present
- **Auth**: None (public API)
- See: `references/apis/world-bank-wits.md`

### UK Trade Tariff
- **Data**: UK tariff rates and regulations
- **Coverage**: UK-specific
- See: `references/apis/uk-trade-tariff.md`

### Global Trade Alert
- **Data**: Trade policy changes (70,000+ interventions)
- **Coverage**: 50+ jurisdictions, 2009-present
- See: `references/apis/global-trade-alert.md`

### US Tariffs API
- **Data**: US HTS codes, tariff rates, Section 301 duties
- **Coverage**: US-specific
- See: `references/apis/tariffs-api-us.md`

## Domain Knowledge

- `references/domain/hs-codes.md` - HS code system, chapters, revisions
- `references/domain/trade-terminology.md` - FOB, CIF, MFN, trade balance
- `references/domain/tariff-types.md` - Ad valorem, specific, AVE
- `references/domain/trade-flows.md` - Import/export concepts
- `references/domain/country-codes.md` - ISO, Comtrade codes

## Integration Patterns

- `references/patterns/multi-source-aggregation.md` - Combining APIs
- `references/patterns/data-normalization.md` - Harmonizing formats
- `references/patterns/rate-limiting-strategies.md` - Managing quotas
