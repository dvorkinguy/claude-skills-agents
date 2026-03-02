# Grafana Alerting Guide

## Alert Rule Structure

### Prometheus Alerting Rule
```yaml
groups:
  - name: GroupName
    interval: 1m
    rules:
      - alert: AlertName
        expr: |
          your_promql_expression > threshold
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Brief description"
          description: "Detailed description with {{ $value }}"
          runbook_url: "https://wiki.example.com/runbook"
```

## Severity Levels

| Level | Use Case | Response Time | Notification |
|-------|----------|---------------|--------------|
| `critical` | Service down, data loss risk | Immediate | Page + Email |
| `warning` | Degradation, approaching limits | Hours | Slack/Telegram |
| `info` | Informational, tracking | None | Dashboard only |

## Common Alert Patterns

### High CPU Usage
```yaml
- alert: HighCPUUsage
  expr: |
    100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High CPU on {{ $labels.instance }}"
    description: "CPU at {{ printf \"%.1f\" $value }}%"
```

### High Memory Usage
```yaml
- alert: HighMemoryUsage
  expr: |
    100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 85
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High memory on {{ $labels.instance }}"
```

### Disk Space Low
```yaml
- alert: LowDiskSpace
  expr: |
    100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100)
    / node_filesystem_size_bytes{mountpoint="/"}) > 85
  for: 10m
  labels:
    severity: warning
```

### Instance Down
```yaml
- alert: InstanceDown
  expr: up == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "{{ $labels.job }} is down"
```

### HTTP Endpoint Down
```yaml
- alert: ServiceDown
  expr: probe_success == 0
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "{{ $labels.instance }} is down"
```

### High Latency
```yaml
- alert: HighLatency
  expr: probe_duration_seconds > 2
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High latency for {{ $labels.instance }}"
    description: "Response time: {{ printf \"%.2f\" $value }}s"
```

### SSL Certificate Expiring
```yaml
- alert: SSLCertExpiringSoon
  expr: (probe_ssl_earliest_cert_expiry - time()) / 86400 < 14
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "SSL cert expires in {{ printf \"%.0f\" $value }} days"
```

### Container Restart Loop
```yaml
- alert: ContainerRestarting
  expr: increase(container_restart_count{name!=""}[15m]) > 0
  for: 0m
  labels:
    severity: warning
  annotations:
    summary: "Container {{ $labels.name }} is restarting"
```

### Container OOM Killed
```yaml
- alert: ContainerOOMKilled
  expr: container_oom_events_total > 0
  for: 0m
  labels:
    severity: critical
  annotations:
    summary: "{{ $labels.name }} was OOM killed"
```

## `for` Duration Guidelines

| Scenario | Recommended `for` |
|----------|-------------------|
| Complete outage | 1-2m |
| Degradation | 5-10m |
| Capacity warnings | 10-15m |
| Trend-based | 30m+ |

## Alertmanager Configuration

### Route Configuration
```yaml
route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'
```

### Inhibition Rules
```yaml
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']
```

### Silences
Use for planned maintenance:
```bash
amtool silence add alertname="Watchdog" --duration=2h --comment="Maintenance window"
```

## Notification Templates

### Telegram
```
{{ define "telegram.message" }}
{{ if eq .Status "firing" }}🔥{{ else }}✅{{ end }} {{ .CommonAnnotations.summary }}

{{ range .Alerts }}
• {{ .Annotations.description }}
{{ end }}
{{ end }}
```

### Email
```html
{{ define "email.html" }}
<h2>{{ .Status | toUpper }}</h2>
<table>
{{ range .Alerts }}
<tr>
  <td><strong>{{ .Labels.alertname }}</strong></td>
  <td>{{ .Annotations.description }}</td>
</tr>
{{ end }}
</table>
{{ end }}
```

## Testing Alerts

### Unit Testing with promtool
```yaml
# alert_test.yml
rule_files:
  - alerts.yml
tests:
  - interval: 1m
    input_series:
      - series: 'up{job="test"}'
        values: '0 0 0 0 0'
    alert_rule_test:
      - eval_time: 5m
        alertname: InstanceDown
        exp_alerts:
          - exp_labels:
              job: test
              severity: critical
```

Run with: `promtool test rules alert_test.yml`

## Best Practices

1. **Avoid alert fatigue**: Set appropriate thresholds and `for` durations
2. **Group related alerts**: Use `group_by` in Alertmanager
3. **Include runbooks**: Link to documentation in annotations
4. **Use templating**: Make alerts actionable with context
5. **Test regularly**: Ensure alerts fire when expected
6. **Review periodically**: Remove stale alerts, adjust thresholds
