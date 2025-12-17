# ROI Calculation Formulas

## Core Formula

```
ROI = (Gain from Investment - Cost of Investment) / Cost of Investment × 100
```

For automation:
```
Monthly ROI = (Monthly Savings - Monthly Cost) / Monthly Cost × 100
Annual ROI = (Annual Savings - Total First Year Cost) / Total First Year Cost × 100
```

---

## Labor Cost Savings

### Formula
```
Monthly Labor Savings = Hours Saved × Hourly Rate × 4.33 (weeks/month)
```

### Fully Loaded Hourly Rate
Don't use base salary. Use fully loaded cost:

```
Fully Loaded Rate = (Annual Salary + Benefits + Overhead) / 2,080 hours

Benefits = Salary × 25-35% (health, retirement, taxes)
Overhead = Salary × 10-20% (space, equipment, management)

Example:
$60,000 salary
+ $18,000 benefits (30%)
+ $9,000 overhead (15%)
= $87,000 / 2,080 = $42/hr fully loaded
```

### Quick Multiplier
```
Hourly Rate = Annual Salary / 2,080 × 1.4 (approximate fully loaded)

$60,000 / 2,080 × 1.4 = $40.38/hr
```

---

## Error Cost Savings

### Formula
```
Monthly Error Cost = Tasks × Error Rate × Cost per Error

Where:
- Tasks = number of manual operations per month
- Error Rate = % that have errors (typically 1-5% for data entry)
- Cost per Error = rework time + customer impact + penalties
```

### Common Error Costs
| Error Type | Typical Cost |
|------------|--------------|
| Data entry mistake | $25-50 (fix time) |
| Missed deadline | $100-500 (rush fees, penalties) |
| Wrong shipment | $50-200 (return, reship) |
| Compliance error | $500-10,000+ (fines, audit) |
| Customer error (churn) | Lifetime value × churn probability |

### Example
```
Monthly invoices: 200
Error rate: 3%
Cost per error: $75 (30 min fix + customer call)

Error Cost = 200 × 0.03 × $75 = $450/month
```

---

## Opportunity Cost

### Formula
```
Opportunity Cost = Hours Freed × Value of Alternative Activity
```

### Common Scenarios
| Current Activity | Alternative Activity | Value Multiplier |
|-----------------|---------------------|------------------|
| Admin work | Sales calls | 3-5x |
| Data entry | Client service | 2-3x |
| Reporting | Strategy | 2-4x |
| Support tickets | Product development | 2-3x |

### Example
```
Salesperson doing 10 hrs/week admin
Hourly rate: $50
If doing sales instead: 3x value

Opportunity Cost = 10 × $50 × 3 × 4.33 = $6,495/month
```

---

## Revenue Impact

### Formula
```
Revenue Impact = Volume Increase × Value per Unit
             OR = Conversion Improvement × Total Pipeline × Avg Deal Size
```

### Examples

**Faster Response Time:**
```
Current: 2hr avg response, 10% conversion
Automated: 5min response, 15% conversion
Monthly leads: 100
Avg deal: $1,000

Before: 100 × 10% × $1,000 = $10,000
After: 100 × 15% × $1,000 = $15,000
Impact: $5,000/month
```

**Reduced Cart Abandonment:**
```
Monthly carts: 1,000
Current recovery: 5%
Automated recovery: 15%
Avg cart: $150

Before: 1,000 × 5% × $150 = $7,500 recovered
After: 1,000 × 15% × $150 = $22,500 recovered
Impact: $15,000/month
```

---

## Payback Period

### Formula
```
Payback Period = Total Investment / Monthly Savings

Where:
- Total Investment = Setup Cost + (Monthly Cost × Months until ROI)
```

### Simple Calculation
```
Setup: $2,000
Monthly: $500
Monthly Savings: $2,000

Months to Break Even = $2,000 / ($2,000 - $500) = 1.33 months
```

### With Ramp-Up
```
Month 1: 50% effectiveness
Month 2: 75% effectiveness
Month 3+: 100% effectiveness

Adjusted savings = Sum of (Monthly Savings × Effectiveness)
```

---

## Total Cost of Ownership (TCO)

### Formula
```
3-Year TCO = Setup + (Monthly × 36) + Training + Maintenance + Updates
```

### Components
| Component | Typical Range |
|-----------|---------------|
| Setup/Implementation | 1-3 months of service |
| Monthly service | Base price |
| Training | 5-10% of setup |
| Maintenance | 10-20% annually |
| Updates/Changes | 5-15% annually |

---

## ROI Presentation Templates

### Conservative Estimate
```
Monthly waste identified: $5,000
Automation captures: 70% (conservative)
Monthly savings: $3,500
Your investment: $700/month
Net monthly gain: $2,800
Annual ROI: 400%
```

### Range Estimate
```
                    Low      Mid      High
Savings identified: $3,000   $5,000   $7,000
Capture rate:       60%      75%      90%
Monthly savings:    $1,800   $3,750   $6,300
Your investment:    $700     $700     $700
Net gain:           $1,100   $3,050   $5,600
Annual ROI:         157%     436%     800%
```

### Break-Even Analysis
```
Setup investment: $3,000
Monthly service: $500
Monthly savings: $2,000

Payback: 2 months
Year 1 net gain: ($2,000 × 12) - $3,000 - ($500 × 12) = $15,000
Year 2+ annual gain: ($2,000 - $500) × 12 = $18,000
```

---

## Quick Reference Benchmarks

### Automation Savings by Task Type
| Task Type | Typical Savings |
|-----------|----------------|
| Data entry | 80-95% |
| Report generation | 70-90% |
| Notifications | 90-99% |
| Document routing | 75-90% |
| Follow-ups | 85-95% |
| Scheduling | 60-80% |

### Pricing as % of Value
| Relationship | Price Target |
|--------------|--------------|
| One-time project | 20-30% of year 1 savings |
| Monthly retainer | 15-25% of monthly savings |
| Value share | 10-20% of realized savings |

### Minimum Viable ROI
- Client should see **3x ROI minimum** to feel good
- Aim for **5x ROI** in proposals (gives room for negotiation)
- **10x ROI** is a no-brainer deal
