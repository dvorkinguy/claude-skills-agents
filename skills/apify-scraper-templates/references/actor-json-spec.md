# actor.json Specification

The `actor.json` file is the main configuration for an Apify Actor. It must be located in the `.actor/` directory.

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `actorSpecification` | integer | Always `1` |
| `name` | string | Actor name (lowercase, hyphens allowed) |
| `version` | string | Format: `N.N` (e.g., `0.0`, `1.0`, `2.5`) |

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `buildTag` | string | `latest` | Tag applied to successful builds |
| `dockerfile` | string | (auto-detect) | Path to Dockerfile relative to `.actor/` |
| `input` | string/object | - | Path to input schema or embedded schema |
| `readme` | string | - | Path to Actor README |
| `minMemoryMbytes` | integer | 256 | Minimum memory allocation |
| `maxMemoryMbytes` | integer | 4096 | Maximum memory allocation |
| `environmentVariables` | object | - | Build-time environment variables |
| `usesStandbyMode` | boolean | false | Enable standby mode for faster starts |
| `storages` | object | - | Schema definitions for dataset/key-value store |

## Full Example

```json
{
    "actorSpecification": 1,
    "name": "my-web-scraper",
    "version": "1.0",
    "buildTag": "latest",
    "minMemoryMbytes": 512,
    "maxMemoryMbytes": 8192,
    "dockerfile": "./Dockerfile",
    "input": "./input_schema.json",
    "readme": "./README.md",
    "environmentVariables": {
        "NODE_ENV": "production",
        "API_KEY": "@mySecretApiKey"
    },
    "storages": {
        "dataset": "./dataset_schema.json"
    },
    "usesStandbyMode": false
}
```

## Environment Variables

Environment variables can reference Apify secrets using the `@` prefix:

```json
{
    "environmentVariables": {
        "PUBLIC_VAR": "plain-value",
        "SECRET_VAR": "@myApifySecret"
    }
}
```

Secrets must be created in Apify Console under Settings > Secrets.

## Memory Settings

| Memory | Use Case |
|--------|----------|
| 256 MB | Simple HTTP scrapers, CheerioCrawler |
| 512 MB | Standard Crawlee scrapers |
| 1024 MB | PlaywrightCrawler with moderate data |
| 2048 MB | Heavy Playwright/Puppeteer usage |
| 4096+ MB | Large-scale crawls, data processing |

## Dockerfile Auto-Detection

If `dockerfile` is not specified, Apify searches in order:
1. `.actor/Dockerfile`
2. `./Dockerfile` (project root)

## Version Format

The version must follow the `N.N` format:
- Valid: `0.0`, `1.0`, `2.5`, `10.99`
- Invalid: `1.0.0`, `v1.0`, `1`, `latest`

Each push can optionally increment the version:
```bash
apify push --version 1.1
```

## Input Schema Reference

The `input` field can be:

**Path to external file:**
```json
{
    "input": "./input_schema.json"
}
```

**Embedded schema:**
```json
{
    "input": {
        "title": "My Input",
        "type": "object",
        "schemaVersion": 1,
        "properties": {
            "url": {
                "title": "URL",
                "type": "string",
                "editor": "textfield"
            }
        }
    }
}
```

## Dataset Schema

Define output structure in `storages.dataset`:

```json
{
    "storages": {
        "dataset": {
            "actorSpecification": 1,
            "title": "Product Dataset",
            "views": {
                "overview": {
                    "title": "Overview",
                    "transformation": {
                        "fields": ["title", "price", "url"]
                    },
                    "display": {
                        "component": "table",
                        "properties": {
                            "title": {"label": "Product Title"},
                            "price": {"label": "Price", "format": "currency"},
                            "url": {"label": "URL", "format": "link"}
                        }
                    }
                }
            }
        }
    }
}
```

## Standby Mode

Enable for faster cold starts (experimental):

```json
{
    "usesStandbyMode": true
}
```

Standby mode keeps a warm container ready, reducing startup time from ~10s to ~1s.

## Validation Checklist

- [ ] `actorSpecification` is `1`
- [ ] `name` is lowercase with hyphens only
- [ ] `version` follows `N.N` format
- [ ] `minMemoryMbytes` <= `maxMemoryMbytes`
- [ ] Dockerfile exists at specified path
- [ ] Input schema path is valid (if specified)
- [ ] Secret references use `@` prefix
