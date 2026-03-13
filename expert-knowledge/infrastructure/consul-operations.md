# Consul Operations & Best Practices (XNAi Foundation)

**Status**: 🟢 CURRENT  
**Last Updated**: 2026-02-28  
**Owner**: MC-Overseer  
**Domain**: Infrastructure

---

## Overview

In the XNAi Foundation stack, **HashiCorp Consul** (v1.15.4) serves as the primary Service Discovery and Health Monitoring engine. It is configured in a single-node, single-server mode (`bootstrap-expect=1`) optimized for the AMD Ryzen 5700U environment.

---

## 🛠 Deployment Configuration

The Consul service is deployed via Docker/Podman with the following critical parameters:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `image` | `consul:1.15.4` | Stable version |
| `bootstrap-expect` | `1` | Enables single-node server mode |
| `client` | `0.0.0.0` | Allows API/UI access from other containers |
| `data_dir` | `/consul/data` | Persistent storage location |
| `ports` | `8500, 8600/udp` | UI/API and DNS ports |

### Persistence (CRITICAL)
Always ensure `./data/consul` is mounted to `/consul/data:Z`. Without this, all KV data and service registrations are lost on container restart.

---

## 🛡 Security & Hardening

### 1. ACL System (Access Control)
By default, the XNAi stack should enforce ACLs to prevent unauthorized service registration or KV access.
- **Default Policy**: `deny`
- **Management Token**: Generate via `consul acl bootstrap` and store in `secrets/consul_master_token.txt`.

### 2. Gossip Encryption
Enable gossip encryption to secure internal communication:
```hcl
encrypt = "YOUR_BASE64_KEY"
```

### 3. Rootless Podman
Consul runs as the `root` user inside the container by default in the official image, but the XNAi stack uses `:Z` volume flags to handle SELinux/permission mapping.

---

## 📈 Operational Workflows

### 1. Health Monitoring
Consul monitors all stack services via HTTP or TCP checks defined in `docker-compose.yml`.
- **UI Access**: [http://localhost:8500](http://localhost:8500)
- **Check Status**: Use `consul monitor` or the UI to view real-time health transitions.

### 2. Backup & Recovery (Fast Recovery Strategy)
Since there is no failover in a 1-node setup, backups are vital.
```bash
# Manual Snapshot
docker exec xnai_consul consul snapshot save /consul/data/backup.snap

# Restore Snapshot
docker exec xnai_consul consul snapshot restore /consul/data/backup.snap
```

### 3. Service Registration
Services should register themselves via the Consul API (port 8500).
```bash
# Example Registration
curl --request PUT --data @service.json http://localhost:8500/v1/agent/service/register
```

---

## ⚠️ Known Issues & Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| No Leader Elected | `bootstrap-expect` > 1 or data corruption | Ensure `bootstrap-expect=1` and check volume health. |
| ACL Permission Denied | Missing or invalid token | Provide `X-Consul-Token` header in API requests. |
| High CPU Usage | Large catalog or frequent health checks | Increase check intervals or optimize KV watch patterns. |

---

## 📚 References
- [Consul Official Docs](https://developer.hashicorp.com/consul/docs)
- [XNAi Infrastructure Strategy](memory_bank/strategies/production-tight-stack/PLAN-PRODUCTION-TIGHT-STACK.md)
