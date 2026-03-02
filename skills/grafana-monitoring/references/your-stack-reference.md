# Your Stack Reference

Complete reference for your Oracle Cloud monitoring infrastructure.

## Infrastructure Overview

### Server Details
| Property | Value |
|----------|-------|
| Provider | Oracle Cloud Free Tier |
| Region | Jerusalem |
| IP | 129.159.149.15 |
| User | ubuntu |
| Access | SSH key-based |

### URLs
| Service | URL |
|---------|-----|
| Grafana | https://grafana.guydvorkin.com |
| Coolify | https://coolify.guydvorkin.com |
| n8n | https://n8n.guydvorkin.com |

## Monitoring Stack

### Docker Services (docker-compose.monitoring.yml)
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| prometheus | prom/prometheus:latest | 9090 | Metrics storage |
| grafana | grafana/grafana:latest | 3000 | Dashboards |
| loki | grafana/loki:2.9.0 | 3100 | Log aggregation |
| alertmanager | prom/alertmanager:latest | 9093 | Alert routing |
| node-exporter | prom/node-exporter:latest | 9100 | Host metrics |
| cadvisor | gcr.io/cadvisor/cadvisor | 8081 | Container metrics |
| blackbox-exporter | prom/blackbox-exporter:latest | 9115 | HTTP probes |
| promtail | grafana/promtail:2.9.0 | 9080 | Log shipper |

### Data Retention
- Prometheus: 15 days
- Loki: 15 days (configurable)

## Prometheus Configuration

### Scrape Jobs
```yaml
scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ['localhost:9090']

  - job_name: node
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: cadvisor
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: blackbox-http
    metrics_path: /probe
    params:
      module: [http_2xx]
    file_sd_configs:
      - files: ['/etc/prometheus/targets/blackbox-targets.yml']
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

### HTTP Targets (blackbox-targets.yml)
```yaml
# Control Center - Internal
- targets:
    - 'grafana:3000'
    - 'coolify:8080'
  labels:
    project: control-center
    type: internal

# Control Center - External
- targets:
    - 'https://grafana.guydvorkin.com'
    - 'https://coolify.guydvorkin.com'
    - 'https://n8n.guydvorkin.com'
  labels:
    project: control-center
    type: external

# Client Projects
- targets:
    - 'https://exportarena.com'
    - 'https://api.exportarena.com'
    - 'https://app.exportarena.com'
  labels:
    project: exportarena

- targets:
    - 'https://afarsemon.com'
  labels:
    project: afarsemon

- targets:
    - 'https://surp.ai'
  labels:
    project: surpai

- targets:
    - 'https://biocbt.com'
  labels:
    project: biocbt
```

## Dashboards

### HTTP Probes Dashboard (http-probes)
**Purpose**: Monitor endpoint availability and latency

**Key Panels**:
- Endpoint Status Overview (table)
- Project Latency Graphs
- SSL Certificate Expiry
- Uptime History

**Variables**: None (shows all)

### Infrastructure Overview (infrastructure-overview)
**Purpose**: Server and container resource monitoring

**Key Panels**:
- CPU/Memory/Disk Gauges
- System Uptime
- Resource Time Series
- Network I/O
- Container Metrics

**Variables**: None

### Health Status 10K v3 (health-status-10k-v2)
**Purpose**: High-level health summary (executive view)

**Key Panels**:
- Overall System Status
- Endpoints UP count
- Resource Gauges
- Project Status Cards
- Infrastructure Status

**Variables**: `$project` (filter by project)

## Alert Rules

### Node Alerts
| Alert | Threshold | Duration | Severity |
|-------|-----------|----------|----------|
| HighCPUUsage | >80% | 5min | warning |
| CriticalCPUUsage | >95% | 2min | critical |
| HighMemoryUsage | >85% | 5min | warning |
| CriticalMemoryUsage | >95% | 2min | critical |
| LowDiskSpace | >85% | 10min | warning |
| CriticalDiskSpace | >95% | 5min | critical |
| InstanceDown | up==0 | 1min | critical |
| LowCPUUsageWarning | <15% (6h) | 6h | warning |

**Note**: LowCPUUsageWarning helps prevent Oracle Free Tier reclamation.

### Container Alerts
| Alert | Condition | Severity |
|-------|-----------|----------|
| ContainerDown | not seen 60s | critical |
| ContainerHighCPU | >80% | warning |
| ContainerHighMemory | >85% | warning |
| ContainerRestarting | restart in 15min | warning |
| ContainerOOMKilled | OOM event | critical |

### HTTP Alerts
| Alert | Threshold | Severity |
|-------|-----------|----------|
| ServiceDown | probe_success==0 | critical |
| HighLatency | >2s | warning |
| VeryHighLatency | >5s | critical |
| SSLCertExpiringSoon | <14 days | warning |
| SSLCertExpiringCritical | <7 days | critical |
| HTTPStatusError | status>=400 | warning |

## Alertmanager Routes

### Receivers
| Receiver | Type | Target |
|----------|------|--------|
| critical-alerts | Telegram + Email | Both channels |
| telegram-alerts | Telegram | Telegram bot |
| email-alerts | Email | SMTP |
| null-receiver | None | Silence |

### Routing
- `severity: critical` → critical-alerts
- `severity: warning` → telegram-alerts
- `channel: email` → email-alerts

## Log Collection (Promtail)

### Sources
```yaml
scrape_configs:
  - job_name: containers
    static_configs:
      - targets: [localhost]
        labels:
          job: containerlogs
          __path__: /var/lib/docker/containers/*/*log

  - job_name: system
    static_configs:
      - targets: [localhost]
        labels:
          job: varlogs
          __path__: /var/log/*log

  - job_name: syslog
    static_configs:
      - targets: [localhost]
        labels:
          job: syslog
          __path__: /var/log/syslog

  - job_name: coolify
    static_configs:
      - targets: [localhost]
        labels:
          job: coolify
          __path__: /data/coolify/**/*.log
```

## Common Queries for Your Stack

### CPU Usage
```promql
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

### Memory Usage
```promql
100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))
```

### Disk Usage
```promql
100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"})
```

### All Endpoints Status
```promql
probe_success{job="blackbox-http"}
```

### SSL Days Remaining
```promql
(probe_ssl_earliest_cert_expiry - time()) / 86400
```

### Container CPU by Name
```promql
sum(rate(container_cpu_usage_seconds_total{name!=""}[5m])) by (name) * 100
```

### Container Memory
```promql
container_memory_usage_bytes{name!=""} / 1024 / 1024
```

### Error Logs
```logql
{container_name=~".+"} |= "error" | logfmt
```

### Grafana Logs
```logql
{container_name="grafana"} | json
```

## Maintenance Commands

### SSH Access
```bash
ssh ubuntu@129.159.149.15
```

### Service Management
```bash
cd /data/monitoring
docker compose -f docker-compose.monitoring.yml restart grafana
docker compose -f docker-compose.monitoring.yml logs -f prometheus
```

### Prometheus Reload
```bash
curl -X POST http://localhost:9090/-/reload
```

### Check Alert Rules
```bash
docker exec prometheus promtool check rules /etc/prometheus/alert-rules/*.yml
```
