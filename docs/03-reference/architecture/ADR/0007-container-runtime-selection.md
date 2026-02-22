# ADR 0007: Container Runtime Selection (Podman)

## Status
Accepted

## Context
The XNAi Foundation Stack is designed for sovereignty and offline-first operation. The container runtime choice impacts security, deployment flexibility, and resource requirements. Key requirements:
- Rootless execution for security
- No daemon dependency for reliability
- Docker-compatible CLI and compose files
- Works on Linux without special kernel requirements

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **Podman** | Rootless, daemonless, Docker-compatible, OCI-compliant | Slightly different volume handling |
| **Docker** | Industry standard, huge ecosystem | Requires daemon, root by default |
| **Docker Rootless** | Rootless mode exists | Complex setup, some limitations |
| **containerd** | Lightweight, Kubernetes-native | Less user-friendly, nerdctl needed |
| **LXC/LXD** | System containers, lightweight | Different paradigm, less app-focused |
| **NixOS containers** | Declarative, reproducible | Nix-specific, learning curve |

## Decision
We adopt **Podman** as the primary container runtime:

**Key Factors:**
1. **Rootless by Default**: Runs as unprivileged user (UID 1001)
2. **Daemonless**: No single point of failure, better reliability
3. **Docker-Compatible**: `podman` and `podman-compose` are drop-in replacements
4. **OCI-Compliant**: Standard container format, portable
5. **SELinux Integration**: Works with `:Z` and `:U` volume labels

**Deployment Pattern:**
```yaml
services:
  rag:
    user: "${APP_UID:-1001}:${APP_GID:-1001}"
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    volumes:
      - ./data:/app/data:Z  # SELinux label
```

## Consequences

### Positive
- **Security**: No root daemon, reduced attack surface
- **Reliability**: No daemon to crash or restart
- **Sovereignty**: No Docker Hub account required
- **Compatibility**: `alias docker=podman` works for most commands
- **User Namespaces**: Proper isolation with `subuid`/`subgid`

### Negative
- **Volume Permissions**: Requires `:Z` or `:U` for SELinux
- **Compose Differences**: `podman-compose` has minor differences
- **Learning Curve**: Users familiar with Docker need adjustment
- **Mac/Windows**: Podman Desktop different experience

### Security Comparison

| Feature | Docker (root) | Docker (rootless) | Podman |
|---------|---------------|-------------------|--------|
| Root daemon | Yes | No | No |
| Container root = host root | Yes | No | No |
| User namespaces | Optional | Yes | Default |
| SELinux support | Yes | Limited | Full |
| Rootless network | Limited | Limited | Full (slirp4netns) |

## Implementation Notes

### Volume Permission Pattern
```bash
# Rootless Podman volume handling
podman unshare chown 1001:1001 ./data
# Or use :U flag for automatic ownership
podman run -v ./data:/app/data:U ...
```

### Systemd Integration (Quadlet)
```ini
# /etc/containers/systemd/xnai-rag.container
[Container]
Image=localhost/xnai-rag:latest
User=1001
Volume=./data:/app/data:Z

[Service]
Restart=always
```

## Related
- `expert-knowledge/environment/rootless_podman_u_flag.md`
- `expert-knowledge/architect/podman_rootless_permissions.md`
- `docs/03-how-to-guides/hardware-tuning/`
