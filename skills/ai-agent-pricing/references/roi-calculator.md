# ROI Calculator

## Quick Calculator

### Time Savings ROI

```
INPUTS:
Hours saved per week:        [____]
Weeks per year:              52
Hourly rate (fully loaded):  $[____]

CALCULATION:
Annual hours saved:     hours × 52 = [____]
Annual value:           hours × rate = $[____]

Your price:             $[____]/year
ROI:                    (value - price) / price × 100 = [____]%
Payback period:         price / (value ÷ 365) = [____] days
```

### Error Reduction ROI

```
INPUTS:
Errors per month (before):   [____]
Cost per error:              $[____]
Error reduction rate:        [____]%

CALCULATION:
Errors eliminated/mo:   errors × reduction% = [____]
Monthly savings:        eliminated × cost = $[____]
Annual savings:         monthly × 12 = $[____]
```

### Revenue Increase ROI

```
INPUTS:
Additional leads/month:      [____]
Conversion rate:             [____]%
Average deal value:          $[____]

CALCULATION:
New customers/month:    leads × rate = [____]
Monthly revenue:        customers × value = $[____]
Annual revenue:         monthly × 12 = $[____]
```

## Combined ROI Template

```markdown
# ROI Analysis: [Client Name]

## Current State (Monthly)
| Metric | Value |
|--------|-------|
| Hours on [task] | X hrs |
| Hourly cost | $Y |
| Errors/mistakes | Z |
| Cost per error | $A |
| Missed opportunities | B |
| Value per opportunity | $C |

## Projected Improvement
| Metric | Improvement |
|--------|-------------|
| Time reduction | X% |
| Error reduction | Y% |
| Opportunity capture | Z% |

## Monthly Value Created
| Category | Calculation | Value |
|----------|-------------|-------|
| Time savings | X hrs × $Y × Z% | $[A] |
| Error reduction | B errors × $C × D% | $[E] |
| Revenue increase | F leads × G% × $H | $[I] |
| **Total Monthly** | | **$[J]** |

## Investment
| Item | Cost |
|------|------|
| Setup (one-time) | $[K] |
| Monthly service | $[L] |
| First year total | K + (L × 12) = $[M] |

## ROI Summary
- First year value: $[J × 12]
- First year cost: $[M]
- Net benefit: $[value - cost]
- ROI: [(value - cost) / cost × 100]%
- Payback period: [M / J] months
```

## Industry Benchmarks

### Time Savings by Task Type
| Task | Typical Hours Saved/Week |
|------|--------------------------|
| Data entry | 10-20 hrs |
| Email triage | 5-15 hrs |
| Report generation | 3-8 hrs |
| Lead qualification | 5-10 hrs |
| Invoice processing | 3-5 hrs |
| Customer support | 10-30 hrs |

### Hourly Rates (Fully Loaded)
| Role | Range |
|------|-------|
| Admin assistant | $25-40/hr |
| Sales rep | $50-80/hr |
| Marketing | $60-100/hr |
| Developer | $80-150/hr |
| Executive | $150-300/hr |

### Error Cost Benchmarks
| Error Type | Typical Cost |
|------------|--------------|
| Data error | $50-200 |
| Missed deadline | $200-1,000 |
| Customer complaint | $100-500 |
| Compliance issue | $1,000-10,000+ |
| Lost sale | Deal value × 0.5 |

## Presentation Tips

### Visual Format
```
+------------------+     +------------------+
| WITHOUT AGENT    |     | WITH AGENT       |
+------------------+     +------------------+
| 40 hrs/week      | --> | 8 hrs/week       |
| 15 errors/month  | --> | 2 errors/month   |
| $8,000/mo cost   | --> | $2,500/mo cost   |
+------------------+     +------------------+

            SAVINGS: $5,500/mo
            YOUR INVESTMENT: $697/mo
            NET GAIN: $4,803/mo
```

### Credibility Boosters
- "Conservative estimate (actual likely higher)"
- "Based on [similar client] data"
- "Guaranteed minimum or your money back"

### Urgency Creators
- "Each month you wait costs $[X]"
- "That's $[X/30] per day you're losing"
- "Over the year, that's $[X×12]"

## Spreadsheet Export

```csv
Category,Before,After,Improvement,Monthly Value
Hours on Task,[X],[Y],[X-Y],"[savings × hourly rate]"
Error Rate,[A]%,[B]%,[A-B]%,"[errors × cost reduction]"
Response Time,[C] hrs,[D] hrs,[C-D] hrs,"[value of faster response]"
```

## Calculator Script

For interactive calculation, use:
```bash
python scripts/roi_calculator.py --hours 20 --rate 75 --errors 10 --error-cost 100
```

Output:
```
ROI Analysis
============
Time Savings:    $78,000/year
Error Reduction: $12,000/year
Total Value:     $90,000/year

At $9,000/year investment:
ROI: 900%
Payback: 37 days
```
