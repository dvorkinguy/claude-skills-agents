# Trade Flows

## Flow Types

### Imports (M)
Goods entering a country's customs territory for domestic consumption.

```
Flow Code: M
Direction: Inward
Valuation: Usually CIF
```

**Includes:**
- Direct imports for consumption
- Imports for processing
- Imports into free zones (varies)

**Excludes:**
- Transit goods
- Temporary imports (usually)

### Exports (X)
Goods leaving a country's customs territory.

```
Flow Code: X
Direction: Outward
Valuation: Usually FOB
```

**Includes:**
- Domestic production exports
- Re-exports (sometimes separate)

**Excludes:**
- Transit goods
- Temporary exports (usually)

### Re-Exports (RX)
Foreign goods exported without substantial transformation.

```
Flow Code: RX
Direction: Outward (of foreign goods)
```

**Example:**
```
Computer chips imported to Singapore
→ Re-exported to Thailand (no manufacturing)
```

**Common in:**
- Trading hubs (Singapore, Hong Kong, Dubai)
- Entrepôt trade
- Free trade zones

### Re-Imports (RM)
Domestic goods returned from abroad.

```
Flow Code: RM
Direction: Inward (of domestic goods)
```

**Common reasons:**
- Goods returned after processing abroad
- Returned unsold goods
- Goods re-imported after repair
- Failed export transactions

## Trade System Concepts

### General Trade System
Records all goods entering/leaving the economic territory.
- Includes free zone flows
- Broader coverage
- Used by: USA, Netherlands, UK

### Special Trade System
Records goods entering/leaving the domestic consumption area.
- Excludes free zone flows (until cleared)
- Narrower coverage
- Used by: Most countries

### Impact on Data
```
General trade > Special trade

Free zone imports:
- General: Recorded at entry
- Special: Recorded when cleared for domestic use
```

## Data Reporting

### Reporter vs Partner Perspective

**Reporter's Imports:**
```
Israel imports from China
Reporter: Israel (376)
Partner: China (156)
Flow: M (Import)
```

**Partner's Exports (Mirror):**
```
China exports to Israel
Reporter: China (156)
Partner: Israel (376)
Flow: X (Export)
```

### Mirror Data Usage

**Comparing reports:**
```
Israel reports: Import from China = $5.0B
China reports: Export to Israel = $4.8B

Discrepancy = $0.2B (4%)
```

**Common reasons for discrepancy:**
1. CIF vs FOB valuation (~5-10%)
2. Different recording time
3. Country of origin vs last shipment
4. Confidentiality suppression
5. Threshold differences
6. Classification differences

### Typical CIF/FOB Ratio
```
CIF / FOB ≈ 1.05 to 1.15

Varies by:
- Distance (longer = higher ratio)
- Product type (bulky = higher)
- Mode of transport (sea vs air)
```

## Data Quality Issues

### Under-reporting
- Informal/smuggled trade
- Below threshold transactions
- Tax evasion

### Over-reporting
- Carousel fraud (VAT schemes)
- Transfer pricing manipulation
- Multiple counting in transit

### Transit Issues
```
Product: Made in China
Route: China → Hong Kong → Israel

Hong Kong reports:
- Import from China
- Re-export to Israel

Could be counted multiple times if not handled correctly.
```

## Seasonal Patterns

### Agricultural Products
- Harvest seasons affect export timing
- Counter-seasonal trade (Southern/Northern hemisphere)

### Consumer Goods
- Pre-holiday imports surge (Q3-Q4)
- Post-holiday returns (Q1)

### Raw Materials
- Price-driven stockpiling
- Contract timing effects

## Trade Balance Calculation

### Bilateral Balance
```python
def bilateral_balance(reporter, partner, year):
    exports = get_trade(reporter, partner, 'X', year)
    imports = get_trade(reporter, partner, 'M', year)
    return exports - imports
```

### Total Balance
```python
def total_balance(reporter, year):
    total_exports = get_trade(reporter, 0, 'X', year)  # Partner 0 = World
    total_imports = get_trade(reporter, 0, 'M', year)
    return total_exports - total_imports
```

### Goods vs Services
```
Trade Balance (goods) + Trade Balance (services) = Current Account (trade portion)
```

Note: UN Comtrade = goods only. Services from WTO or national sources.

## Aggregation Levels

### By Partner
```
Reporter: Israel
Partner: World (0) → Total trade
Partner: USA (842) → Bilateral trade
```

### By Product
```
cmdCode: TOTAL → All goods
cmdCode: 85 → Chapter 85 (electrical)
cmdCode: 8517 → Heading (telephones)
```

### By Time
```
freqCode: A → Annual
freqCode: M → Monthly
```

## Interpretation Tips

### Gross vs Net Flows
```
Gross exports = Total shipments
Net exports = Exports - Re-imports

For some analysis, net flows more meaningful.
```

### Value vs Volume
```
Value change could be due to:
- Price change (unit value)
- Volume change (quantity)

Check both for complete picture.
```

### Concentration Indices
```
HHI = Σ(share_i)²

High HHI = concentrated trade (few partners/products)
Low HHI = diversified trade
```
