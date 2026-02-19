---
priority: critical
context: general
activation: always
last_updated: 2026-02-17
version: 2.0
---

# Dependency Management

## Core Philosophy
Lock files over ranges for reproducibility, security, and stability.

## Tool Priority
1. **uv** (preferred): Fast, secure, modern
2. **pip-tools**: Complex resolution with hashes
3. **pip**: Fallback only

## Container-Only Operations
**ALL pip/uv operations in Podman containers only**
Never install packages directly on host system.

```bash
# Standard pattern
podman run --rm -v $(pwd):/workspace:Z,U -w /workspace \
  python:3.12-slim bash -c "
    curl -LsSf https://astral.sh/uv/install.sh | sh &&
    export PATH=\"\$HOME/.local/bin:\$PATH\" &&
    uv pip compile --generate-hashes requirements.in
  "
```

## Hash Verification
```bash
# Generate with cryptographic hashes
uv pip compile --generate-hashes requirements.in --output-file requirements.txt

# Install from lock file
uv pip sync requirements.txt
```

## Version Strategy
| Environment | Strategy | Example |
|-------------|----------|---------|
| Production | Exact versions | `==1.2.3` |
| Development | Compatible releases | `~=1.2.0` |
| Security | Immediate updates | CVE patches |

## Package Sources
- **Primary**: PyPI
- **Mirrors**: `pypi.mirrors.ustc.edu.cn`, `pypi.sdutlinux.org`
- **Security**: Verify signatures when available

## Common Conflicts
| Package | Issue | Resolution |
|---------|-------|------------|
| MkDocs plugins | Strict versions | Check plugin compatibility |
| Material theme | MkDocs core conflicts | Pin both explicitly |
| Pydantic | Breaking changes | Use major version pin |
| Async libraries | AnyIO/structlog | Test thoroughly |

## Update Commands
```bash
# Check updates (dry run)
uv lock --upgrade --dry-run

# Update specific package
uv lock --upgrade-package package-name

# View dependency tree
uv tree

# Check for outdated
uv pip list --outdated

# Security check
uv pip check
```

## Emergency Protocol
1. **Immediate**: Revert to last working lock file
2. **Investigate**: Identify root cause
3. **Temp fix**: Use `--override package==1.2.3`
4. **Permanent**: Update constraints
5. **Document**: Record incident

## Checklist
- [ ] All operations in containers
- [ ] Lock files with hashes
- [ ] Volume mounts use `:Z,U`
- [ ] Non-root containers (`USER 1001`)
- [ ] CI validates lock files
- [ ] Weekly dependency audits
