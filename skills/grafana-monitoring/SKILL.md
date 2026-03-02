---
name: grafana-monitoring
description: Grafana monitoring and observability toolkit. Use when working with Grafana dashboards, Prometheus queries (PromQL), Loki logs (LogQL), alerting rules, incident management, or monitoring infrastructure. Supports dashboard CRUD, metric analysis, log exploration, alert configuration, and annotation management.
---

# Grafana Monitoring Toolkit

Comprehensive monitoring operations using Grafana MCP tools.

## MCP Tool Decision Tree

### Discovery Phase
| Need | Tool | Example |
|------|------|---------|
| Search dashboards | `search_dashboards` | Search by title/tag |
| List datasources | `list_datasources` | Get available datasources |
| Get dashboard | `get_dashboard_by_uid` | Retrieve full JSON |
| Dashboard summary | `get_dashboard_summary` | Token-efficient overview |

### Query Phase
| Need | Tool | Example |
|------|------|---------|
| Prometheus query | `query_prometheus` | Execute PromQL |
| Loki query | `query_loki` | Execute LogQL |
| Metric metadata | `list_prometheus_metric_metadata` | Get metric info |
| Label values | `list_prometheus_label_values` | Get label options |

### Modification Phase
| Need | Tool | Example |
|------|------|---------|
| Update dashboard | `update_dashboard` | Full dashboard update |
| Patch dashboard | `patch_dashboard` | Partial update |
| Create annotation | `create_annotation` | Add event markers |

### Alerting Phase
| Need | Tool | Example |
|------|------|---------|
| List alert rules | `list_alert_rules` | Get all rules |
| Get alert rule | `get_alert_rule_by_uid` | Specific rule details |
| List contact points | `list_contact_points` | Notification channels |

## PromQL Cookbook

### CPU Metrics
```promql
# CPU usage percentage (instant)
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# CPU by mode
sum by(mode) (rate(node_cpu_seconds_total[5m])) * 100

# Load average normalized
node_load15 / count without(cpu, mode) (node_cpu_seconds_total{mode="idle"})
```

### Memory Metrics
```promql
# Memory usage percentage
100 * (1 - ((node_memory_MemAvailable_bytes) / (node_memory_MemTotal_bytes)))

# Memory available GB
node_memory_MemAvailable_bytes / 1024 / 1024 / 1024

# Memory pressure
node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
```

### Disk Metrics
```promql
# Disk usage percentage
100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"})

# Disk I/O rate
rate(node_disk_read_bytes_total[5m]) + rate(node_disk_written_bytes_total[5m])
```

### Network Metrics
```promql
# Network receive rate
rate(node_network_receive_bytes_total{device!="lo"}[5m])

# Network transmit rate
rate(node_network_transmit_bytes_total{device!="lo"}[5m])
```

### Container Metrics (cAdvisor)
```promql
# Container CPU usage
sum(rate(container_cpu_usage_seconds_total{name!=""}[5m])) by (name) * 100

# Container memory usage
container_memory_usage_bytes{name!=""} / 1024 / 1024

# Container restarts
increase(container_restart_count{name!=""}[1h])
```

### HTTP Probe Metrics (Blackbox)
```promql
# Probe success
probe_success{job="blackbox-http"}

# Response time
probe_duration_seconds{job="blackbox-http"}

# SSL certificate expiry (days)
(probe_ssl_earliest_cert_expiry - time()) / 86400

# HTTP status code
probe_http_status_code{job="blackbox-http"}
```

## LogQL Cookbook

### Container Logs
```logql
# All logs from a container
{container_name="grafana"}

# Error level logs
{container_name=~".+"} |= "error" | logfmt

# JSON parsed logs
{container_name="n8n"} | json | level="error"
```

### System Logs
```logql
# Auth failures
{filename="/var/log/auth.log"} |= "Failed"

# SSH connections
{filename="/var/log/auth.log"} |= "sshd"

# System errors
{filename="/var/log/syslog"} |= "error" | logfmt
```

### Rate and Aggregations
```logql
# Error rate per minute
sum(rate({container_name=~".+"} |= "error" [1m])) by (container_name)

# Log volume by container
sum by (container_name) (rate({container_name=~".+"} [5m]))
```

## Your Stack Reference

### Infrastructure
- **Server**: Oracle Cloud (ubuntu@129.159.149.15)
- **Grafana URL**: https://grafana.guydvorkin.com
- **Prometheus**: http://prometheus:9090
- **Loki**: http://loki:3100

### Scrape Jobs
| Job | Target | Port | Metrics |
|-----|--------|------|---------|
| prometheus | localhost | 9090 | Self-monitoring |
| node | node-exporter | 9100 | Host metrics |
| cadvisor | cadvisor | 8080 | Container metrics |
| blackbox-http | blackbox-exporter | 9115 | HTTP probes |
| blackbox-ssl | blackbox-exporter | 9115 | SSL certs |
| grafana | grafana | 3000 | Grafana metrics |
| loki | loki | 3100 | Loki metrics |

### Dashboards
| UID | Name | Purpose |
|-----|------|---------|
| http-probes | HTTP Probes - All Projects | Endpoint monitoring |
| infrastructure-overview | Infrastructure Overview | Server/container metrics |
| health-status-10k-v2 | Health Status 10K v3 | High-level health view |

### Alert Groups
- **NodeAlerts**: CPU, memory, disk, instance down
- **ContainerAlerts**: Container health, CPU, memory, restarts
- **HTTPAlerts**: Service down, latency, SSL expiry

### Projects Monitored
| Project | Endpoints |
|---------|-----------|
| ExportArena | exportarena.com, api.exportarena.com |
| Afarsemon | afarsemon.com |
| Surp.ai | surp.ai |
| BioCBT | biocbt.com |
| Coolify Services | coolify, n8n, grafana |

## Dashboard JSON Structure

### Panel Types
```json
{
  "type": "stat",        // Single value display
  "type": "gauge",       // Circular gauge
  "type": "timeseries",  // Time-based graph
  "type": "table",       // Tabular data
  "type": "text",        // Markdown/HTML
  "type": "row"          // Collapsible section
}
```

### Common Panel Structure
```json
{
  "id": 1,
  "title": "Panel Title",
  "type": "timeseries",
  "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
  "datasource": {"type": "prometheus", "uid": "prometheus"},
  "targets": [
    {
      "expr": "your_promql_query",
      "legendFormat": "{{label}}",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percent",
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "green", "value": null},
          {"color": "yellow", "value": 70},
          {"color": "red", "value": 90}
        ]
      }
    }
  }
}
```

### Variable Definition
```json
{
  "templating": {
    "list": [
      {
        "name": "project",
        "type": "custom",
        "query": "exportarena,afarsemon,surpai,biocbt",
        "current": {"text": "All", "value": "$__all"}
      }
    ]
  }
}
```

## Alert Rules Structure

### Prometheus Alert Rule
```yaml
groups:
  - name: NodeAlerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ printf \"%.2f\" $value }}%"
```

### Alert Severity Levels
- `critical`: Immediate action required (pages on-call)
- `warning`: Investigation needed (Telegram notification)
- `info`: Informational only

## Validation Checklist

### Dashboard Creation
- [ ] Unique dashboard UID
- [ ] All panels have datasource specified
- [ ] Queries return data
- [ ] Thresholds set appropriately
- [ ] Variables defined for filtering

### Alert Rules
- [ ] `for` duration appropriate (avoid flapping)
- [ ] Labels include severity
- [ ] Annotations provide context
- [ ] Tested with real data

### PromQL Queries
- [ ] Rate/increase used for counters
- [ ] Appropriate time windows
- [ ] Labels for disambiguation
- [ ] Tested in Explore first

## Scripts

### Validate Dashboard JSON
```bash
python scripts/validate_dashboard.py dashboard.json
```

### Lint PromQL Query
```bash
python scripts/promql_lint.py "your_query_here"
```

## References

| Topic | File |
|-------|------|
| MCP Tools (50+) | `references/mcp-tools-guide.md` |
| PromQL Patterns | `references/promql-patterns.md` |
| LogQL Patterns | `references/logql-patterns.md` |
| Dashboard JSON | `references/dashboard-json-spec.md` |
| Alerting Guide | `references/alerting-guide.md` |
| Your Stack | `references/your-stack-reference.md` |

## Templates

### Dashboards
- `assets/templates/dashboards/http-probes-template.json`
- `assets/templates/dashboards/infrastructure-template.json`
- `assets/templates/dashboards/health-10k-template.json`

### Alerts
- `assets/templates/alerts/node-alerts-template.yml`
- `assets/templates/alerts/container-alerts-template.yml`
