# PromQL Patterns Reference

## Counter vs Gauge

### Counters (always increasing)
Use `rate()` or `increase()`:
```promql
# Rate per second over 5 minutes
rate(http_requests_total[5m])

# Total increase over 1 hour
increase(http_requests_total[1h])
```

### Gauges (can go up or down)
Use directly or with aggregations:
```promql
# Current value
node_memory_MemAvailable_bytes

# Average over time
avg_over_time(node_memory_MemAvailable_bytes[1h])
```

## Aggregation Functions

### sum, avg, min, max, count
```promql
# Sum by label
sum by (job) (rate(http_requests_total[5m]))

# Average across all
avg(node_memory_MemAvailable_bytes)

# Count unique label values
count by (status_code) (http_requests_total)
```

### without vs by
```promql
# Include only these labels
sum by (job, instance) (up)

# Exclude these labels (keep rest)
sum without (cpu, mode) (node_cpu_seconds_total)
```

## Time Functions

### rate vs irate
```promql
# rate: average rate (smoother)
rate(http_requests_total[5m])

# irate: instant rate (more responsive, noisier)
irate(http_requests_total[5m])
```

### Subqueries
```promql
# Max of hourly rates over past day
max_over_time(rate(http_requests_total[1h])[24h:1h])
```

## Label Matching

### Operators
```promql
# Exact match
up{job="prometheus"}

# Regex match
up{job=~"prometheus|grafana"}

# Regex not match
up{job!~"test.*"}

# Not equal
up{job!="test"}
```

## Binary Operations

### Arithmetic
```promql
# Memory usage percentage
100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))
```

### Comparison
```promql
# Filter to values > 80
node_cpu_seconds_total > 80

# Keep original values where condition true
node_cpu_seconds_total and on() (hour() >= 9 and hour() <= 17)
```

### Vector Matching
```promql
# One-to-one matching
http_requests_total / on(job, instance) http_request_duration_sum

# Many-to-one matching
up * on(job) group_left(version) job_metadata
```

## Common Patterns

### Availability/Uptime
```promql
# Service availability %
avg_over_time(up[24h]) * 100

# Probe success rate
avg by (instance) (probe_success) * 100
```

### Saturation
```promql
# CPU saturation (load > cores)
node_load1 > on(instance) count by(instance) (node_cpu_seconds_total{mode="idle"})
```

### Error Rate
```promql
# Error percentage
sum(rate(http_requests_total{status=~"5.."}[5m]))
/ sum(rate(http_requests_total[5m])) * 100
```

### Request Latency
```promql
# P99 latency using histogram
histogram_quantile(0.99, sum(rate(http_request_duration_bucket[5m])) by (le))

# Average latency
rate(http_request_duration_sum[5m]) / rate(http_request_duration_count[5m])
```

### Growth Prediction
```promql
# Disk full in X hours
predict_linear(node_filesystem_avail_bytes[6h], 24*3600) < 0
```

## Recording Rules

Pre-compute expensive queries:
```yaml
groups:
  - name: performance
    interval: 30s
    rules:
      - record: job:http_requests:rate5m
        expr: sum by(job) (rate(http_requests_total[5m]))
```

## Gotchas

1. **Missing data**: Use `or vector(0)` for fallback
2. **Label conflicts**: Use `on()` for explicit matching
3. **Counter resets**: `rate()` handles resets automatically
4. **Staleness**: Data goes stale after 5 minutes
5. **Time alignment**: Use `@` modifier for specific timestamps
