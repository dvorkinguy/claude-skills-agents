# Harmonized System (HS) Codes

## Overview

The Harmonized System is an international nomenclature for classifying traded products. Developed by the World Customs Organization (WCO), it's used by over 200 countries.

## Code Structure

```
XX          Chapter (2-digit)     - Broad category
XXXX        Heading (4-digit)     - More specific
XXXXXX      Subheading (6-digit)  - International standard
XXXXXXXX    National (8-digit)    - Country-specific
XXXXXXXXXX  Tariff line (10-digit) - Most detailed
```

### Example Breakdown
```
85          Chapter: Electrical machinery
8517        Heading: Telephones
851712      Subheading: Smartphones
85171210    US HTS: Smartphones with LCD
8517121000  Full tariff line
```

## HS Chapters (Sections I-XXI)

### Section I: Live Animals; Animal Products (01-05)
- 01: Live animals
- 02: Meat and edible meat offal
- 03: Fish and crustaceans
- 04: Dairy produce, eggs, honey
- 05: Products of animal origin

### Section II: Vegetable Products (06-14)
- 06: Live trees and plants
- 07: Edible vegetables
- 08: Edible fruit and nuts
- 09: Coffee, tea, spices
- 10: Cereals
- 11: Milling products
- 12: Oil seeds
- 13: Lac, gums, resins
- 14: Vegetable plaiting materials

### Section III: Fats and Oils (15)
- 15: Animal or vegetable fats and oils

### Section IV: Food, Beverages, Tobacco (16-24)
- 16: Preparations of meat/fish
- 17: Sugars and sugar confectionery
- 18: Cocoa and preparations
- 19: Cereal preparations
- 20: Vegetable preparations
- 21: Miscellaneous food preparations
- 22: Beverages, spirits, vinegar
- 23: Food industry residues
- 24: Tobacco

### Section V: Mineral Products (25-27)
- 25: Salt, sulphur, earths, stone
- 26: Ores, slag, ash
- 27: Mineral fuels, oils

### Section VI: Chemical Products (28-38)
- 28: Inorganic chemicals
- 29: Organic chemicals
- 30: Pharmaceutical products
- 31: Fertilizers
- 32: Tanning/dyeing extracts
- 33: Essential oils, perfumery
- 34: Soap, waxes
- 35: Albuminoidal substances
- 36: Explosives
- 37: Photographic goods
- 38: Miscellaneous chemical products

### Section VII: Plastics and Rubber (39-40)
- 39: Plastics
- 40: Rubber

### Section VIII: Leather and Skins (41-43)
- 41: Raw hides and skins
- 42: Leather articles
- 43: Furskins

### Section IX: Wood and Cork (44-46)
- 44: Wood and articles
- 45: Cork
- 46: Manufactures of straw

### Section X: Paper (47-49)
- 47: Pulp of wood
- 48: Paper and paperboard
- 49: Printed books, newspapers

### Section XI: Textiles (50-63)
- 50: Silk
- 51: Wool
- 52: Cotton
- 53: Other vegetable textile fibers
- 54: Man-made filaments
- 55: Man-made staple fibers
- 56: Wadding, felt
- 57: Carpets
- 58: Special woven fabrics
- 59: Impregnated textile fabrics
- 60: Knitted fabrics
- 61: Knitted apparel
- 62: Woven apparel
- 63: Other textile articles

### Section XII: Footwear, Headgear (64-67)
- 64: Footwear
- 65: Headgear
- 66: Umbrellas
- 67: Prepared feathers

### Section XIII: Stone, Ceramics, Glass (68-70)
- 68: Stone, plaster, cement
- 69: Ceramic products
- 70: Glass

### Section XIV: Precious Metals/Stones (71)
- 71: Pearls, precious stones, precious metals

### Section XV: Base Metals (72-83)
- 72: Iron and steel
- 73: Articles of iron/steel
- 74: Copper
- 75: Nickel
- 76: Aluminum
- 78: Lead
- 79: Zinc
- 80: Tin
- 81: Other base metals
- 82: Tools
- 83: Miscellaneous metal articles

### Section XVI: Machinery and Electronics (84-85)
- 84: Machinery, mechanical appliances
- 85: Electrical machinery

### Section XVII: Vehicles (86-89)
- 86: Railway vehicles
- 87: Motor vehicles
- 88: Aircraft
- 89: Ships

### Section XVIII: Optical, Medical (90-92)
- 90: Optical, photographic, medical instruments
- 91: Clocks and watches
- 92: Musical instruments

### Section XIX: Arms (93)
- 93: Arms and ammunition

### Section XX: Miscellaneous Manufactured (94-96)
- 94: Furniture
- 95: Toys, games, sports
- 96: Miscellaneous manufactured articles

### Section XXI: Works of Art (97)
- 97: Works of art, collectors' pieces

## HS Revisions

| Version | Year | Code |
|---------|------|------|
| H0 | 1992 | Original |
| H1 | 1996 | 1st revision |
| H2 | 2002 | 2nd revision |
| H3 | 2007 | 3rd revision |
| H4 | 2012 | 4th revision |
| H5 | 2017 | 5th revision |
| H6 | 2022 | 6th revision (current) |

## National Extensions

### US HTS (Harmonized Tariff Schedule)
- 8-10 digits
- First 6 digits = international HS
- Additional digits for US-specific

### EU CN (Combined Nomenclature)
- 8 digits
- Used for EU trade statistics

### TARIC (EU)
- 10 digits
- Includes tariff rates

## Using HS Codes in APIs

### UN Comtrade
```python
# 2-digit chapter
cmdCode='85'

# 4-digit heading
cmdCode='8517'

# 6-digit subheading
cmdCode='851712'

# Multiple codes
cmdCode='8517,8471'

# All under chapter
cmdCode='85*'

# Total trade
cmdCode='TOTAL'
```

### World Bank WITS
```
/product/850000  # 6-digit with padding
/product/all     # All products
```

## Special Codes

| Code | Meaning |
|------|---------|
| TOTAL | Aggregate all products |
| AG | Agricultural products |
| NOAG | Non-agricultural |
| 999999 | Confidential/unclassified |
