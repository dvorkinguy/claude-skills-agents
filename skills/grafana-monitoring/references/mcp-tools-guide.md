# Grafana MCP Tools Reference

Complete reference for all 50+ Grafana MCP tools.

## Search & Navigation

### search_dashboards
Search dashboards by title or tag.
```
search_dashboards(query: "http", tag: "infrastructure")
```

### generate_grafana_url
Generate deeplinks with time ranges.
```
generate_grafana_url(dashboard_uid: "http-probes", from: "now-6h", to: "now")
```

## Dashboards

### get_dashboard_by_uid
Retrieve full dashboard JSON.
```
get_dashboard_by_uid(uid: "http-probes")
```
**Warning**: Large context consumption. Use `get_dashboard_summary` for overviews.

### get_dashboard_summary
Token-efficient dashboard overview.
```
get_dashboard_summary(uid: "http-probes")
```

### get_dashboard_property
Extract specific data using JSONPath.
```
get_dashboard_property(uid: "http-probes", path: "$.panels[0].title")
```

### update_dashboard
Full dashboard update (overwrites).
```
update_dashboard(dashboard: {...full JSON...})
```

### patch_dashboard
Partial dashboard update.
```
patch_dashboard(uid: "http-probes", changes: {"title": "New Title"})
```

## Datasources

### list_datasources
List all configured datasources.
```
list_datasources()
```

### get_datasource_by_uid
Get specific datasource details.
```
get_datasource_by_uid(uid: "prometheus")
```

### get_datasource_by_name
Get datasource by name.
```
get_datasource_by_name(name: "Prometheus")
```

## Prometheus

### query_prometheus
Execute PromQL query.
```
query_prometheus(
  datasource_uid: "prometheus",
  expr: "up",
  time: "now",
  timeout: "30s"
)
```

### query_prometheus_range
Execute range query.
```
query_prometheus_range(
  datasource_uid: "prometheus",
  expr: "rate(node_cpu_seconds_total[5m])",
  start: "now-1h",
  end: "now",
  step: "1m"
)
```

### list_prometheus_metric_metadata
Get metric metadata.
```
list_prometheus_metric_metadata(datasource_uid: "prometheus", metric: "node_cpu_seconds_total")
```

### list_prometheus_metric_names
List all metric names.
```
list_prometheus_metric_names(datasource_uid: "prometheus")
```

### list_prometheus_label_values
Get values for a label.
```
list_prometheus_label_values(datasource_uid: "prometheus", label: "job")
```

## Loki

### query_loki
Execute LogQL query.
```
query_loki(
  datasource_uid: "loki",
  query: "{container_name=\"grafana\"} |= \"error\"",
  limit: 100,
  start: "now-1h",
  end: "now"
)
```

### list_loki_label_names
List all Loki labels.
```
list_loki_label_names(datasource_uid: "loki")
```

### list_loki_label_values
Get values for a Loki label.
```
list_loki_label_values(datasource_uid: "loki", label: "container_name")
```

### get_loki_stats
Get Loki stream statistics.
```
get_loki_stats(datasource_uid: "loki")
```

## Alerting

### list_alert_rules
List all alert rules.
```
list_alert_rules()
```

### get_alert_rule_by_uid
Get specific alert rule.
```
get_alert_rule_by_uid(uid: "rule-uid")
```

### list_contact_points
List notification contact points.
```
list_contact_points()
```

## Incidents

### list_incidents
List active incidents.
```
list_incidents(status: "active")
```

### create_incident
Create new incident.
```
create_incident(
  title: "Service Down",
  severity: "critical",
  labels: {"team": "platform"}
)
```

### get_incident
Get incident details.
```
get_incident(incident_id: "123")
```

### add_incident_activity
Add activity to incident.
```
add_incident_activity(incident_id: "123", body: "Investigating root cause")
```

## OnCall

### list_oncall_schedules
List on-call schedules.
```
list_oncall_schedules()
```

### get_oncall_schedule
Get schedule details.
```
get_oncall_schedule(schedule_id: "456")
```

### list_oncall_shifts
List shifts for a schedule.
```
list_oncall_shifts(schedule_id: "456")
```

### list_oncall_teams
List on-call teams.
```
list_oncall_teams()
```

## Annotations

### create_annotation
Create annotation (event marker).
```
create_annotation(
  dashboard_uid: "http-probes",
  time: "now",
  text: "Deployment completed",
  tags: ["deploy", "v1.2.3"]
)
```

### list_annotations
List annotations.
```
list_annotations(dashboard_uid: "http-probes", from: "now-24h", to: "now")
```

### update_annotation
Update existing annotation.
```
update_annotation(annotation_id: 789, text: "Updated text")
```

### delete_annotation
Delete annotation.
```
delete_annotation(annotation_id: 789)
```

## Admin Tools (Disabled by Default)

### list_teams
List all teams.

### list_users
List all users.

### list_roles
List available roles.

### get_permissions
Get permission details.

## Best Practices

1. **Context Management**: Use `get_dashboard_summary` instead of `get_dashboard_by_uid` for large dashboards
2. **Query Testing**: Test PromQL/LogQL in Explore before using in dashboards
3. **Time Ranges**: Always specify explicit time ranges for reproducibility
4. **Error Handling**: Check for empty results before processing
5. **Rate Limiting**: Space out requests when doing bulk operations
