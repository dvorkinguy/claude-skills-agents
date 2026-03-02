# Trade Terminology

## Valuation Terms

### FOB (Free on Board)
Value of goods at the exporting country's port, including:
- Product cost
- Inland transport to port
- Loading onto vessel

**Used for**: Export statistics

### CIF (Cost, Insurance, Freight)
Value including:
- FOB value
- International shipping
- Insurance

**Used for**: Import statistics

### Relationship
```
CIF = FOB + Freight + Insurance
CIF ≈ FOB × 1.05 to 1.15 (typical markup)
```

### Why It Matters
- Exports typically reported FOB
- Imports typically reported CIF
- Creates "CIF/FOB discrepancy" in global trade data
- World exports ≠ World imports (due to shipping costs)

## Trade Partners

### Reporter
Country reporting the trade data.
```
Reporter: Israel → Reports Israel's imports from China
```

### Partner
Trading partner country.
```
Partner: China → The country Israel trades with
```

### Mirror Data
Same trade from partner's perspective:
```
Israel reports: Import from China = $5B
China reports: Export to Israel = $4.8B (mirror)
```

**Uses for mirror data:**
- Validate data quality
- Fill gaps in reporting
- Detect discrepancies

### Partner Codes
| Code | Meaning |
|------|---------|
| 0 | World (all partners) |
| 896 | Areas not elsewhere specified |
| 899 | Areas not specified |

## Tariff Terms

### MFN (Most Favored Nation)
Default tariff rate applied to WTO members.
- "Non-discriminatory" treatment
- Same rate for all MFN partners
- Used when no preferential agreement exists

### Preferential Tariff
Reduced rate under trade agreements:
- **FTA**: Free Trade Agreement (often 0%)
- **GSP**: Generalized System of Preferences (for developing countries)
- **Customs Union**: Common external tariff

### Bound Rate
Maximum tariff committed at WTO.
```
Bound rate: 15%
Applied rate: 8%
Margin: 7% (can raise up to 15%)
```

### Applied Rate
Actual tariff charged at customs.
- Must be ≤ bound rate
- Can vary by partner (preferential)

### AVE (Ad Valorem Equivalent)
Converting non-ad valorem tariffs to percentage:
```
Specific tariff: $2/kg
Average price: $20/kg
AVE = $2 / $20 = 10%
```

## Trade Flows

### Imports (M)
Goods entering the country.
- Usually valued CIF
- Subject to import tariffs
- Recorded at customs entry

### Exports (X)
Goods leaving the country.
- Usually valued FOB
- May have export duties (rare)
- Recorded at customs exit

### Re-exports (RX)
Foreign goods exported without substantial transformation.
```
Imported to Hong Kong → Re-exported to mainland China
```

### Re-imports (RM)
Domestic goods returned from abroad.
```
Exported for processing → Re-imported after processing
```

### Transit Trade
Goods passing through without entering domestic economy.
- Often excluded from trade statistics
- Important for hub countries (Singapore, Netherlands)

## Trade Balance

### Calculation
```
Trade Balance = Exports - Imports
```

### Interpretations
| Balance | Term | Meaning |
|---------|------|---------|
| Positive | Trade Surplus | Exports > Imports |
| Negative | Trade Deficit | Imports > Exports |
| Zero | Balanced Trade | Exports = Imports |

### By Partner
```
Israel-China Trade Balance = Israel exports to China - Israel imports from China
```

## Trade Agreements

### Types
| Type | Example | Coverage |
|------|---------|----------|
| FTA | US-Israel FTA | Bilateral goods |
| CU | EU Customs Union | Common external tariff |
| PTA | GSP | Unilateral preferences |
| EIA | EU Single Market | Services, investment |
| BIT | Bilateral Investment Treaty | Investment protection |

### Rules of Origin
Criteria for preferential treatment:
- **Wholly obtained**: Entirely from one country
- **Substantial transformation**: Manufacturing process
- **Value-added**: % of local content
- **Tariff shift**: Change in HS classification

## Data Concepts

### Trade Value
Monetary value of goods traded (usually USD).

### Trade Quantity
Physical amount:
- Weight (kg, tons)
- Units (pieces, pairs)
- Volume (liters, m³)

### Unit Value
```
Unit Value = Trade Value / Quantity
```
Used as price proxy.

### Trade Coverage
What's included in statistics:
- General trade: All goods entering/leaving
- Special trade: Goods entering domestic economy

### Reporting Threshold
Minimum value for recording (varies by country).
```
EU: Intrastat threshold varies by member state
US: EEI required for exports > $2,500
```

## Time Concepts

### Reporting Period
- Annual (A): Calendar year
- Monthly (M): YYYYMM format

### Publication Lag
Time between trade and data availability:
- Preliminary: 2-3 months
- Final/Revised: 6-12 months

### Revision
Updates to previously published data.
- Normal revisions: Improved data
- Major revisions: Methodology changes
