# UN Comtrade API

International merchandise trade statistics from 200+ countries, 1962-present.

## Quick Reference

| Property | Value |
|----------|-------|
| **Library** | `comtradeapicall` (Python) |
| **Install** | `pip install comtradeapicall` |
| **Auth** | Subscription key (free tier available) |
| **Free Limit** | 500 records/call, unlimited calls |
| **Premium Limit** | 250K records/call, 500 calls/day |
| **Portal** | https://comtradedeveloper.un.org |

## Authentication

```python
# Get subscription key from https://comtradedeveloper.un.org
subscription_key = "your-primary-key"  # Use primary or secondary key
```

## Core Functions

### Data Extraction

| Function | Auth Required | Max Records | Use Case |
|----------|---------------|-------------|----------|
| `previewFinalData()` | No | 500 | Quick queries, development |
| `getFinalData()` | Yes | 250,000 | Production data sync |
| `previewTarifflineData()` | No | 500 | Detailed tariff data preview |
| `getTarifflineData()` | Yes | 250,000 | Full tariff line data |
| `getTradeBalance()` | Yes | - | Export/import side-by-side |
| `getBilateralData()` | Yes | - | Compare with mirror data |

### Selection Criteria Parameters

```python
# All data functions accept these parameters:
typeCode      # 'C' (Goods) or 'S' (Services)
freqCode      # 'A' (Annual) or 'M' (Monthly)
clCode        # Classification: 'HS', 'SITC', etc.
period        # YYYY or YYYYMM format
reporterCode  # Country code (e.g., '376' for Israel)
cmdCode       # Product code(s): '91', '91,90', 'TOTAL'
flowCode      # 'X' (Export), 'M' (Import), 'RM', 'RX'
partnerCode   # Trading partner country code
partner2Code  # Secondary partner (optional)
customsCode   # Customs procedure (optional)
motCode       # Transport mode (optional)
```

### Query Options

```python
maxRecords    # Limit results (int)
format_output # 'CSV' or 'JSON'
aggregateBy   # Aggregation method
breakdownMode # 'classic' or 'plus'
countOnly     # Return count only (bool)
includeDesc   # Include descriptions (bool)
```

## Code Examples

### Preview Data (No Auth)

```python
import comtradeapicall

# Australia imports of commodity 91 in May 2022
df = comtradeapicall.previewFinalData(
    typeCode='C',
    freqCode='M',
    clCode='HS',
    period='202205',
    reporterCode='36',
    cmdCode='91',
    flowCode='M',
    partnerCode=None,
    partner2Code=None,
    customsCode=None,
    motCode=None,
    maxRecords=500,
    format_output='JSON',
    aggregateBy=None,
    breakdownMode='classic',
    countOnly=None,
    includeDesc=True
)
```

### Full Data (With Auth)

```python
# Israel imports from all partners
df = comtradeapicall.getFinalData(
    subscription_key,
    typeCode='C',
    freqCode='A',
    clCode='HS',
    period='2023',
    reporterCode='376',  # Israel
    cmdCode='TOTAL',
    flowCode='M',
    partnerCode=None,
    partner2Code=None,
    customsCode=None,
    motCode=None,
    maxRecords=100000,
    format_output='JSON',
    aggregateBy=None,
    breakdownMode='classic',
    countOnly=None,
    includeDesc=True
)
```

### Bulk Download

```python
# Download Morocco final data
comtradeapicall.bulkDownloadFinalFile(
    subscription_key,
    directory='/path/to/save',
    typeCode='C',
    freqCode='A',
    clCode='HS',
    period='2021',
    reporterCode='504',
    decompress=True
)

# Download and combine multiple files
comtradeapicall.bulkDownloadAndCombineFinalFile(
    subscription_key,
    directory='/path/to/save',
    typeCode='C',
    freqCode='M',
    clCode='HS',
    period='202201,202202,202203',
    reporterCode='504',
    decompress=True
)
```

### Trade Balance & Bilateral Data

```python
# Get trade balance (exports and imports side by side)
df = comtradeapicall.getTradeBalance(
    subscription_key,
    typeCode='C',
    freqCode='M',
    clCode='HS',
    period='202205',
    reporterCode='36',
    cmdCode='TOTAL',
    partnerCode=None
)

# Compare reported vs mirror (partner-reported) data
df = comtradeapicall.getBilateralData(
    subscription_key,
    typeCode='C',
    freqCode='M',
    clCode='HS',
    period='202205',
    reporterCode='36',
    cmdCode='TOTAL',
    flowCode='X',
    partnerCode=None
)
```

### Reference Data

```python
# List available references
df = comtradeapicall.listReference()
df = comtradeapicall.listReference('cmd:B5')

# Get specific reference
df = comtradeapicall.getReference('reporter')
df = comtradeapicall.getReference('partner')

# Convert ISO3 to Comtrade codes
codes = comtradeapicall.convertCountryIso3ToCode('USA,FRA,CHE,ITA')
```

### Data Availability

```python
# Check final data availability
df = comtradeapicall.getFinalDataAvailability(
    subscription_key,
    typeCode='C',
    freqCode='A',
    clCode='HS',
    period='2021',
    reporterCode=None
)

# Check bulk file availability
df = comtradeapicall.getFinalDataBulkAvailability(
    subscription_key,
    typeCode='C',
    freqCode='A',
    clCode='S1',
    period='2021',
    reporterCode=None
)

# Get recent releases
df = comtradeapicall.getLiveUpdate(subscription_key)
```

### Async Requests (Large Data)

```python
# Submit async job (up to 2.5M records)
result = comtradeapicall.submitAsyncFinalDataRequest(
    subscription_key,
    typeCode='C',
    freqCode='M',
    clCode='HS',
    period='202205',
    reporterCode='36',
    cmdCode='91,90',
    flowCode='M',
    partnerCode=None,
    partner2Code=None,
    customsCode=None,
    motCode=None,
    aggregateBy=None,
    breakdownMode='classic'
)
print(f"Request ID: {result['requestId']}")

# Check job status
df = comtradeapicall.checkAsyncDataRequest(
    subscription_key,
    batchId='2f92dd59-9763-474c-b27c-4af9ce16d454'
)

# Submit and auto-download when ready
comtradeapicall.downloadAsyncFinalDataRequest(
    subscription_key,
    directory='/path/to/save',
    typeCode='C',
    freqCode='M',
    clCode='HS',
    period='202209',
    reporterCode=None,
    cmdCode='91,90',
    flowCode='M',
    partnerCode=None,
    partner2Code=None,
    customsCode=None,
    motCode=None
)
```

### Metadata & Publication Notes

```python
# Get metadata with publication notes
df = comtradeapicall.getMetadata(
    subscription_key,
    typeCode='C',
    freqCode='M',
    clCode='HS',
    period='202205',
    reporterCode=None,
    showHistory=True
)

# Get Standard Unit Values
df = comtradeapicall.getSUV(
    subscription_key,
    period='2022',
    cmdCode='010391',
    flowCode=None,
    qtyUnitCode=8  # kg
)
```

## Response Fields

| Field | Description |
|-------|-------------|
| `typeCode` | C=Goods, S=Services |
| `freqCode` | A=Annual, M=Monthly |
| `refPeriodId` | YYYY or YYYYMM |
| `reporterCode` | Reporter country code |
| `reporterISO` | Reporter ISO3 code |
| `partnerCode` | Partner country code |
| `partnerISO` | Partner ISO3 code |
| `flowCode` | M=Import, X=Export, RM, RX |
| `cmdCode` | HS product code |
| `cmdDesc` | Product description |
| `primaryValue` | Trade value (USD) |
| `netWgt` | Net weight (kg) |
| `qty` | Quantity |
| `qtyUnitCode` | Quantity unit |

## Proxy Support

All API functions support proxy:

```python
df = comtradeapicall.getFinalData(
    subscription_key,
    typeCode='C',
    # ... other params ...
    proxy_url='http://proxy.example.com:8080'
)
```

## File Naming Convention

Downloaded files follow: `COMTRADE-<DATA>-<TYPE><FREQ><COUNTRY><PERIOD><CLASS>[<DATE>]`

Examples:
- `COMTRADE-FINAL-CM504200003H1[2023-01-03]` - Morocco final data
- `COMTRADE-TARIFFLINE-CM504200003H1[2023-01-03]` - Morocco tariff line

## Key Country Codes

| Country | Code | ISO3 |
|---------|------|------|
| Israel | 376 | ISR |
| USA | 842 | USA |
| China | 156 | CHN |
| World | 0 | WLD |

## Rate Limits

| Tier | Records/Call | Calls/Day |
|------|--------------|-----------|
| Free (Preview) | 500 | Unlimited |
| Free (Subscription) | 100,000 | 500 |
| Premium | 250,000 | Unlimited |
