---
name: coolify-compose
description: >-
    Convert standard Docker Compose files into Coolify-compatible service templates.
    Use when building services for Coolify, converting docker-compose.yml for Coolify deployment, configuring magic credential and URL variables (SERVICE_URL, SERVICE_PASSWORD), or troubleshooting Coolify stack deployments.
---

# Docker Compose in Coolify (Coolify Compose)

Convert standard Docker Compose files into production-ready Coolify templates with automatic credential generation, dynamic Traefik reverse proxy routing, and seamless deployment.

## Two Deployment Modes

Coolify supports two ways to deploy compose stacks:

### 1. Raw Mode (Paste YAML)

Paste YAML directly into the Coolify web interface.

- **Supports:** `image:`, Coolify magic variables, YAML anchors (`&`, `*`), embedded files via `content:`.
- **Does not support:** `build:` directives (requires prebuilt images), external host configuration files.
- **Ideal for:** Quick deployments, standard Docker Hub images without custom build stages.

### 2. Git Repository Mode

Point Coolify to a Git repository containing the compose file and application code.

- **Supports standard Docker Compose features:** `build:` from Dockerfile, relative bind mounts to repository files, Coolify magic variables, and multi-service configurations.
- **Ideal for:** Custom applications with Dockerfiles and checked-in configuration assets.

## Quickstart

Every Coolify template should lead with header metadata comments and magic environment variables:

```yaml
# documentation: https://example.com/docs
# slogan: Concise service description
# category: backend
# tags: api, database, docker
# logo: svgs/my-service.svg
# port: 3000

services:
    app:
        image: myorg/app:latest
        environment:
            - SERVICE_URL_APP_3000 # Generates public URL and routes reverse proxy to port 3000
            - DATABASE_URL=postgres://${SERVICE_USER_POSTGRES}:${SERVICE_PASSWORD_POSTGRES}@db:5432/mydb
        depends_on:
            db:
                condition: service_healthy
        healthcheck:
            test:
                [
                    "CMD",
                    "wget",
                    "-q",
                    "--spider",
                    "http://localhost:3000/health",
                ]
            interval: 5s
            timeout: 10s
            retries: 10

    db:
        image: postgres:16-alpine
        environment:
            - POSTGRES_USER=$SERVICE_USER_POSTGRES
            - POSTGRES_PASSWORD=$SERVICE_PASSWORD_POSTGRES
        healthcheck:
            test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER}"]
            interval: 5s
            timeout: 10s
            retries: 10
```

## Conversion Checklist

When converting a standard `docker-compose.yml`:

1. **Replace static secrets with magic variables:**
    - Change `POSTGRES_PASSWORD=secret123` to `POSTGRES_PASSWORD=$SERVICE_PASSWORD_POSTGRES`.
2. **Replace domain URLs with magic variables:**
    - Add `- SERVICE_URL_APP_3000` and use `APP_URL=$SERVICE_URL_APP`.
3. **Remove `ports:` on proxied services:**
    - Coolify's built-in Traefik handles reverse proxying. Keep `ports:` only if exposing non-HTTP ports directly (SSH, raw TCP/UDP).
4. **Add mandatory Healthchecks:**
    - Coolify depends on healthchecks to determine service readiness and provide zero-downtime rollouts.
5. **Set `depends_on` with health condition:**
    - Use `condition: service_healthy` instead of basic startup ordering.

## Magic Variables Reference

Coolify automatically populates variables matching `SERVICE_<TYPE>_<IDENTIFIER>`:

| Type          | Example                    | Generated Value                                     |
| ------------- | -------------------------- | --------------------------------------------------- |
| `PASSWORD`    | `SERVICE_PASSWORD_DB`      | Secure random password                              |
| `PASSWORD_64` | `SERVICE_PASSWORD_64_KEY`  | 64-character secure random password                 |
| `USER`        | `SERVICE_USER_ADMIN`       | 16-character random username                        |
| `BASE64_64`   | `SERVICE_BASE64_64_SECRET` | 64-character random Base64 string                   |
| `HEX_32`      | `SERVICE_HEX_32_KEY`       | 64-character hex key                                |
| `URL`         | `SERVICE_URL_APP_3000`     | Public URL declaration + proxy routing to port 3000 |
| `FQDN`        | `SERVICE_FQDN_APP`         | Domain only (`app.example.com`), without `https://` |

> [!IMPORTANT]
> **Declaration vs Reference syntax:**
>
> - Declare WITH port: `- SERVICE_URL_APP_3000`
> - Reference WITHOUT port: `APP_URL=$SERVICE_URL_APP`
> - Use hyphens, not underscores, before port numbers: `SERVICE_URL_MY-APP_3000` (valid).

## Native Coolify Extensions

### Automatically Create Directory

```yaml
volumes:
    - type: bind
      source: ./data
      target: /app/data
      is_directory: true
```

### Embed Inline Config File (`content:`)

Useful in Raw Mode (without Git) to inject config files:

```yaml
volumes:
    - type: bind
      source: ./config.json
      target: /app/config.json
      content: |
          {"key": "${SERVICE_PASSWORD_APP}"}
```

### Exclude from Health Check (Migration Containers)

For ephemeral one-shot task containers:

```yaml
services:
    migrate:
        command: ["npm", "run", "migrate"]
        exclude_from_hc: true
```

## Common Troubleshooting

- **"No Available Server" error:** Check container logs and verify that the healthcheck is configured and returning status 200/0.
- **Variables missing in UI:** Use braced syntax `${VARIABLE}` to surface them as editable fields in the Coolify UI.
- **Port routing fails:** Confirm that the port in `SERVICE_URL_APP_PORT` matches the port the container process actually binds to internally, and ensure `ports:` is removed.

## Supporting Documents

- [references/magic-variables.md](references/magic-variables.md) — Comprehensive list of magic variables.
- [references/categories.md](references/categories.md) — Official header category taxonomy.
