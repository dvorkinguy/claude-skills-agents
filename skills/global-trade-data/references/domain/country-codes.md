# Country Codes Reference

## Code Systems

### ISO 3166-1 Alpha-3
Three-letter codes (ISO standard).
```
ISR = Israel
USA = United States
CHN = China
DEU = Germany
```

### ISO 3166-1 Alpha-2
Two-letter codes.
```
IL = Israel
US = United States
CN = China
DE = Germany
```

### UN M49 / Comtrade Codes
Numeric codes used by UN Comtrade.
```
376 = Israel
842 = United States
156 = China
276 = Germany
```

## Key Countries/Regions

### Major Economies
| Country | Comtrade | ISO3 | ISO2 |
|---------|----------|------|------|
| United States | 842 | USA | US |
| China | 156 | CHN | CN |
| Japan | 392 | JPN | JP |
| Germany | 276 | DEU | DE |
| United Kingdom | 826 | GBR | GB |
| France | 251 | FRA | FR |
| India | 699 | IND | IN |
| Italy | 381 | ITA | IT |
| Canada | 124 | CAN | CA |
| South Korea | 410 | KOR | KR |

### Middle East
| Country | Comtrade | ISO3 | ISO2 |
|---------|----------|------|------|
| Israel | 376 | ISR | IL |
| Saudi Arabia | 682 | SAU | SA |
| UAE | 784 | ARE | AE |
| Turkey | 792 | TUR | TR |
| Egypt | 818 | EGY | EG |
| Jordan | 400 | JOR | JO |
| Lebanon | 422 | LBN | LB |
| Iran | 364 | IRN | IR |
| Iraq | 368 | IRQ | IQ |
| Kuwait | 414 | KWT | KW |

### Europe
| Country | Comtrade | ISO3 | ISO2 |
|---------|----------|------|------|
| Netherlands | 528 | NLD | NL |
| Belgium | 56 | BEL | BE |
| Spain | 724 | ESP | ES |
| Poland | 616 | POL | PL |
| Switzerland | 757 | CHE | CH |
| Austria | 40 | AUT | AT |
| Sweden | 752 | SWE | SE |
| Ireland | 372 | IRL | IE |
| Norway | 579 | NOR | NO |
| Denmark | 208 | DNK | DK |

### Asia Pacific
| Country | Comtrade | ISO3 | ISO2 |
|---------|----------|------|------|
| Australia | 36 | AUS | AU |
| Singapore | 702 | SGP | SG |
| Hong Kong | 344 | HKG | HK |
| Taiwan | 490 | TWN | TW |
| Thailand | 764 | THA | TH |
| Malaysia | 458 | MYS | MY |
| Vietnam | 704 | VNM | VN |
| Indonesia | 360 | IDN | ID |
| Philippines | 608 | PHL | PH |
| New Zealand | 554 | NZL | NZ |

### Americas
| Country | Comtrade | ISO3 | ISO2 |
|---------|----------|------|------|
| Mexico | 484 | MEX | MX |
| Brazil | 76 | BRA | BR |
| Argentina | 32 | ARG | AR |
| Chile | 152 | CHL | CL |
| Colombia | 170 | COL | CO |
| Peru | 604 | PER | PE |

## Regional Groups

### World
| Code | Meaning |
|------|---------|
| 0 | World (all countries) |
| WLD | World (ISO) |

### Economic Groups
| Code | Group |
|------|-------|
| 97 | European Union |
| 918 | ASEAN |
| 490 | Developing economies |

### Special Codes
| Comtrade | Meaning |
|----------|---------|
| 0 | World total |
| 97 | EU (as single entity) |
| 896 | Areas not elsewhere specified |
| 899 | Areas not specified |
| 473 | Free zones |
| 536 | Neutral zone |
| 837 | Bunkers |

## Code Conversion

### Python (comtradeapicall)
```python
import comtradeapicall

# ISO3 to Comtrade
code = comtradeapicall.convertCountryIso3ToCode('ISR')
# Returns: 376

# Get all country codes
countries = comtradeapicall.getReference('reporter')
```

### WITS API
```
# Get all countries
GET /wits/datasource/trn/country/ALL

# Response includes:
# - CountryCode
# - Name
# - ISO3
# - ISO2
```

## Historical Changes

### Germany
- Before 1991: DEU (276) = West Germany
- After 1991: DEU (276) = Unified Germany
- DDR (278) = East Germany (historical)

### Yugoslavia
- YUG (890) = Former Yugoslavia
- Split into: SRB, HRV, SVN, BIH, MKD, MNE

### Soviet Union
- SUN (810) = Former USSR
- Split into: RUS, UKR, BLR, KAZ, etc.

### Czechoslovakia
- CSK (200) = Former Czechoslovakia
- Split into: CZE (203), SVK (703)

## EU Membership Timeline

### EU-27 (Current)
Belgium, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Poland, Portugal, Romania, Slovakia, Slovenia, Spain, Sweden

### Brexit
- UK left EU: January 31, 2020
- Transition ended: December 31, 2020

## Tips for Data Analysis

### Handling EU Data
```python
# Trade with EU as single entity
partner_code = 97  # EU aggregate

# Trade with individual EU members
partner_codes = [276, 251, 381, ...]  # DEU, FRA, ITA, etc.

# Note: EU internal trade != EU external trade
```

### China vs Hong Kong
```
China (156) - Mainland China
Hong Kong (344) - Special Administrative Region
Taiwan (490) - Separate customs territory
```

### Re-export Hubs
Watch for data through:
- Hong Kong (344)
- Singapore (702)
- Netherlands (528)
- Belgium (56)

These may show as partners but goods originate elsewhere.
