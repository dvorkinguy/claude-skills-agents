# LogQL Patterns Reference

## Stream Selectors

### Basic Selection
```logql
# By label
{job="varlogs"}

# By container
{container_name="grafana"}

# Multiple labels
{job="varlogs", filename="/var/log/syslog"}
```

### Regex Matching
```logql
# Match pattern
{container_name=~"grafana|prometheus"}

# Exclude pattern
{container_name!~"test.*"}
```

## Line Filters

### Contains
```logql
# Contains "error"
{container_name="app"} |= "error"

# Case insensitive
{container_name="app"} |~ "(?i)error"
```

### Does Not Contain
```logql
# Exclude "debug"
{container_name="app"} != "debug"

# Regex exclude
{container_name="app"} !~ "debug|trace"
```

### Multiple Filters (AND)
```logql
{container_name="app"} |= "error" != "timeout" |= "connection"
```

## Parsers

### logfmt
For logs like: `level=error msg="failed" duration=1.5s`
```logql
{container_name="app"} | logfmt | level="error"
```

### JSON
For JSON logs:
```logql
{container_name="app"} | json | level="error"

# Extract nested field
{container_name="app"} | json | request_id=~".+"
```

### Pattern
For structured text:
```logql
# Apache access log
{job="apache"} | pattern "<ip> - - [<_>] \"<method> <uri> <_>\" <status>"
```

### Regexp
For custom extraction:
```logql
{container_name="app"} | regexp "user=(?P<user>\\w+)"
```

## Label Operations

### keep
```logql
{container_name=~".+"} | json | keep level, msg
```

### drop
```logql
{container_name=~".+"} | json | drop __error__
```

### line_format
```logql
{container_name="app"} | json | line_format "{{.level}}: {{.msg}}"
```

### label_format
```logql
{container_name="app"} | json | label_format new_label=level
```

## Metric Queries

### count_over_time
```logql
# Error count per minute
count_over_time({container_name="app"} |= "error" [1m])
```

### rate
```logql
# Error rate per second
rate({container_name="app"} |= "error" [5m])
```

### sum
```logql
# Total errors by container
sum by (container_name) (count_over_time({container_name=~".+"} |= "error" [1h]))
```

### bytes_over_time
```logql
# Log volume per container
sum by (container_name) (bytes_over_time({container_name=~".+"}[1h]))
```

### unwrap
Extract numeric field:
```logql
# Average duration from logs
avg_over_time({job="app"} | json | unwrap duration [5m])
```

## Common Patterns

### Error Analysis
```logql
# Error count by level
sum by (level) (count_over_time({container_name=~".+"} | json | level=~"error|warn" [1h]))
```

### Request Tracing
```logql
# Follow request by ID
{container_name=~".+"} | json | request_id="abc123"
```

### Security Events
```logql
# Failed logins
{filename="/var/log/auth.log"} |= "Failed password"

# SSH connections
{filename="/var/log/auth.log"} |= "sshd" |= "Accepted"
```

### Container Issues
```logql
# OOM kills
{filename="/var/log/syslog"} |= "oom-kill"

# Container restarts
{container_name=~".+"} |= "restarted"
```

### Performance Issues
```logql
# Slow queries (> 1s)
{container_name="database"} | json | unwrap duration > 1
```

## Time Selection

### Relative
```logql
{job="app"} [5m]   # Last 5 minutes
{job="app"} [1h]   # Last 1 hour
{job="app"} [1d]   # Last 1 day
```

### Absolute (use in Grafana)
Uses `$__range` variable from dashboard time picker.

## Best Practices

1. **Filter early**: Put stream selectors first, then line filters
2. **Parse sparingly**: Only parse when needed (CPU intensive)
3. **Limit results**: Use `limit` for exploration
4. **Use indexes**: Label selectors use index, line filters don't
5. **Aggregate for dashboards**: Use metric queries, not raw logs
