# Caddy Reverse Proxy & Security (XNAi Foundation)

**Status**: 🟢 CURRENT  
**Last Updated**: 2026-02-28  
**Owner**: MC-Overseer  
**Domain**: Infrastructure

---

## Overview

In the XNAi Foundation stack, **Caddy** (v2.8-alpine) acts as the centralized reverse proxy and API gateway. It handles request routing, header security, and provides a unified entry point for the RAG API, Chainlit UI, and Vikunja.

---

## 🛠 Routing & Configuration

The `Caddyfile` defines the following primary routes on port 8000:

| Path Prefix | Backend Service | Purpose |
|-------------|-----------------|---------|
| `/api/v1/*` | `xnai_rag_api:8000` | Foundation RAG API |
| `/` | `xnai_chainlit_ui:8001` | Foundation Chainlit UI |
| `/vikunja/*` | `xnai_vikunja:3456` | Task Management System |
| `/metrics` | `xnai_rag_api:8002` | Prometheus Metrics Scrape Endpoint |

---

## 🛡 Security Hardening

Caddy is configured with standard security headers to protect against common web vulnerabilities:

- **HSTS**: `Strict-Transport-Security "max-age=31536000; includeSubDomains"`
- **Content Type**: `X-Content-Type-Options "nosniff"`
- **Frame Options**: `X-Frame-Options "DENY"` (Prevents clickjacking)
- **XSS Protection**: `X-XSS-Protection "1; mode=block"`
- **Referrer Policy**: `strict-origin-when-cross-origin`

---

## 📈 Operational Workflows

### 1. Health Checks
Caddy monitors the health of the RAG API backend via the `/health` endpoint:
```caddy
reverse_proxy xnai_rag_api:8000 {
  health_uri /health
}
```

### 2. Logging
Access logs are written in JSON format for easy ingestion by the curation worker or ELK/VictoriaMetrics:
- **Location**: `/var/log/caddy/access.log`
- **Format**: Structured JSON

### 3. Reloading Configuration
Caddy supports zero-downtime reloads if the `Caddyfile` is modified:
```bash
docker exec xnai_caddy caddy reload --config /etc/caddy/Caddyfile
```

---

## ⚠️ Known Issues & Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| 502 Bad Gateway | Backend service down | Check `docker ps` and service logs (e.g., `xnai_rag_api`). |
| 404 Not Found | Path prefix mismatch | Verify `uri strip_prefix` logic in `Caddyfile`. |
| SSL Errors | Local trust issues | Ensure `local_trust` is configured or use `internal` certificates. |

---

## 📚 References
- [Caddy Official Docs](https://caddyserver.com/docs/)
- [XNAi Caddyfile](Caddyfile)
