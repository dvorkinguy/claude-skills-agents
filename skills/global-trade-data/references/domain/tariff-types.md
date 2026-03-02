# Tariff Types

## Ad Valorem Tariffs

Percentage of the customs value.

### Structure
```
Duty = Value × Rate
```

### Example
```
Import value: $10,000
Tariff rate: 5%
Duty = $10,000 × 0.05 = $500
```

### Characteristics
- Most common type globally
- Automatic adjustment to price changes
- Easy to compare across products
- Vulnerable to undervaluation fraud

### In Data
```
WITS: AVTariff = 5.0
Type: "AV" or "Ad valorem"
```

## Specific Tariffs

Fixed amount per unit (weight, volume, quantity).

### Structure
```
Duty = Quantity × Rate
```

### Examples
```
$2.00 per kilogram
$0.50 per liter
$15.00 per unit
€5.00 per 100 kg
```

### Calculation
```
Import: 500 kg of sugar
Tariff: $0.30/kg
Duty = 500 × $0.30 = $150
```

### Characteristics
- Fixed cost regardless of price
- Higher effective rate for cheap goods
- Protects against price fluctuations
- Harder to compare across products

### In Data
```
Type: "SP" or "Specific"
Unit: "kg", "l", "u"
```

## Compound Tariffs

Combination of ad valorem and specific.

### Structure
```
Duty = (Value × Ad Valorem Rate) + (Quantity × Specific Rate)
```

### Example
```
Tariff: 5% + $2/kg
Import: $10,000 value, 500 kg

Ad valorem part: $10,000 × 0.05 = $500
Specific part: 500 × $2 = $1,000
Total duty: $500 + $1,000 = $1,500
```

### In Data
```
Type: "CD" or "Compound"
```

## Mixed Tariffs

Either ad valorem OR specific, whichever is higher/lower.

### Types
```
# Minimum tariff (higher of two)
"5% or $2/kg, whichever is greater"

# Maximum tariff (lower of two)
"5% or $2/kg, whichever is less"
```

### In Data
```
Type: "MX" or "Mixed"
```

## Tariff Rate Quota (TRQ)

Different rates based on import volume.

### Structure
```
Within quota: Low rate (often 0%)
Over quota: Higher rate
```

### Example
```
Beef TRQ:
- First 10,000 tons: 0%
- Above 10,000 tons: 40%
```

### In Data
```
Type: "TRQ"
InQuota: 0%
OutQuota: 40%
QuotaVolume: 10000
QuotaUnit: "tons"
```

## Ad Valorem Equivalent (AVE)

Converting all tariffs to percentage equivalent.

### Purpose
- Compare different tariff types
- Calculate average protection
- Policy analysis

### Calculation Methods

**For Specific Tariffs:**
```
AVE = Specific Rate / Unit Value × 100

Example:
Tariff: $2/kg
Average import price: $20/kg
AVE = $2 / $20 × 100 = 10%
```

**For Compound Tariffs:**
```
AVE = Ad Valorem + (Specific / Unit Value × 100)

Example:
Tariff: 5% + $2/kg
Price: $20/kg
AVE = 5 + ($2 / $20 × 100) = 5 + 10 = 15%
```

### AVE Caveats
- Depends on import prices (changes over time)
- Different methods give different results
- UNCTAD TRAINS provides estimated AVEs

### In Data
```
WITS: AVE_Estimated
Comtrade: Not available (calculate from value/quantity)
```

## Seasonal Tariffs

Rates that vary by time of year.

### Example
```
Fresh tomatoes:
- June-September: 5% (domestic harvest)
- October-May: 0% (off-season)
```

## Anti-Dumping Duties

Additional tariff on "dumped" goods (sold below fair value).

### Structure
```
Normal tariff: 5%
AD duty: 25%
Total: 30%
```

### Data Sources
- WTO Anti-dumping database
- Global Trade Alert

## Countervailing Duties

Offset foreign subsidies.

### Structure
```
Normal tariff: 5%
CVD: 15%
Total: 20%
```

## Safeguard Measures

Temporary protection against import surges.

### Example
```
Steel safeguards:
Normal: 0%
Safeguard: 25% (temporary, 3 years)
```

## Section 301 Tariffs (US)

US-specific additional tariffs (notably on China).

### Structure
```
Normal MFN: 5%
Section 301: 25%
Total: 30%
```

### Lists
- List 1: $34B (25%)
- List 2: $16B (25%)
- List 3: $200B (25%)
- List 4A: $120B (7.5%)

## Tariff Rate Summary

| Type | Structure | Example |
|------|-----------|---------|
| Ad Valorem | % of value | 5% |
| Specific | $/unit | $2/kg |
| Compound | % + $/unit | 5% + $2/kg |
| Mixed | % or $/unit | 5% or $2/kg min |
| TRQ In | Low rate | 0% |
| TRQ Out | High rate | 40% |
| AVE | Calculated % | ~10% |
