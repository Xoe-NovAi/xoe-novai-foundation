---
priority: critical
context: general
activation: always
last_updated: 2026-01-27
version: 1.0
---

# Dependency Management & Version Control

**Core Philosophy**: Lock files over ranges for reproducibility, security, and stability. Use modern tools (uv) for speed and reliability.

## 📦 Package Management Rules

### **Tool Selection Priority**
1. **uv** (preferred): Fast, secure, modern Python package manager
2. **pip-tools**: For complex dependency resolution with hashes
3. **pip**: Fallback only, avoid for production dependencies

### **Installation Environment**
- **ALL pip/uv operations in Podman containers only**
- Never install packages directly on host system
- Use volume mounts with `:Z,U` flags for SELinux compatibility
- Non-root containers (`USER 1001`) for security

## 🔒 Security & Integrity

### **Hash Verification**
```bash
# Generate requirements with cryptographic hashes
uv pip compile --generate-hashes requirements.in --output-file requirements.txt

# Or with pip-tools
pip-compile --generate-hashes requirements.in
```

### **Package Sources**
- **Primary**: PyPI with mirrors for reliability
- **Mirrors**: `https://pypi.mirrors.ustc.edu.cn/simple/` or `http://pypi.sdutlinux.org/`
- **Security**: Verify package signatures when available
- **Audit**: Regular dependency vulnerability scanning

### **Version Pinning Strategy**
- **Production**: Exact versions (`==1.2.3`) for reproducibility
- **Development**: Compatible releases (`~=1.2.0`) for flexibility
- **Security**: Immediate updates for CVEs, regardless of breaking changes

## 🐳 Container-Based Operations

### **Standard Podman Command Pattern**
```bash
podman run --rm -v $(pwd):/workspace:Z,U -w /workspace \
  python:3.12-slim bash -c "
    apt-get update && apt-get install -y git curl &&
    curl -LsSf https://astral.sh/uv/install.sh | sh &&
    export PATH=\"\$HOME/.local/bin:\$PATH\" &&
    uv pip compile --generate-hashes requirements.in
  "
```

### **Volume Mount Flags**
- `:Z` - SELinux relabeling for shared volumes
- `:U` - UID/GID mapping for rootless containers
- Use both for maximum compatibility

## 🔄 Dependency Resolution

### **Conflict Resolution Protocol**
1. **Identify Conflict**: Check error messages for conflicting packages
2. **Analyze Dependencies**: Use `uv tree` or `pip-tools` to visualize conflicts
3. **Version Override**: Use `--override` for temporary conflict resolution
4. **Document Changes**: Record all overrides with rationale and expiration date
5. **Test Thoroughly**: Validate functionality after resolution

### **Common Conflict Scenarios**
- **MkDocs Plugins**: Often have strict version requirements
- **Material Theme**: May conflict with MkDocs core versions
- **Pydantic Versions**: Breaking changes between major versions
- **Async Libraries**: Compatibility issues with AnyIO/structlog

## 📋 Maintenance Procedures

### **Regular Updates**
```bash
# Check for updates (dry run)
uv lock --upgrade --dry-run

# Update specific package
uv lock --upgrade-package package-name

# Update all packages (use cautiously)
uv lock --upgrade
```

### **Dependency Auditing**
```bash
# Security vulnerability scan
uv pip check  # Basic compatibility check
# Use external tools like pip-audit for security scanning

# Check for outdated packages
uv pip list --outdated
```

### **Lock File Validation**
- **CI/CD Integration**: Validate lock files on every PR
- **Pre-commit Hooks**: Check for lock file consistency
- **Automated Updates**: Weekly dependency update checks

## 🚨 Emergency Procedures

### **When Dependencies Break**
1. **Immediate**: Revert to last known working lock file
2. **Investigation**: Identify root cause of breakage
3. **Temporary Fix**: Use version overrides if needed
4. **Permanent Solution**: Update constraints or find compatible versions
5. **Documentation**: Record incident and resolution

### **Version Pinning Escape Hatches**
- `--override package==1.2.3` for temporary fixes
- Environment-specific constraints files
- Conditional dependencies based on Python version

## 📊 Monitoring & Metrics

### **Key Metrics to Track**
- **Update Frequency**: Time between dependency updates
- **Security Patches**: Speed of CVE remediation
- **Build Stability**: Lock file conflicts and resolution time
- **Performance**: Dependency resolution time

### **Success Criteria**
- ✅ Zero dependency conflicts in CI/CD
- ✅ All security updates applied within 48 hours
- ✅ Lock files reproducible across environments
- ✅ No host system package pollution

## 🔧 Best Practices

### **Do's**
- ✅ Use lock files for all production deployments
- ✅ Generate hashes for security verification
- ✅ Test dependency updates in isolation
- ✅ Document version constraint rationale
- ✅ Use mirrors for network reliability

### **Don'ts**
- ❌ Never install packages on host system
- ❌ Don't use `--upgrade` without testing
- ❌ Avoid wildcard version ranges (`*`) in production
- ❌ Don't ignore security vulnerabilities
- ❌ Never commit unhashed requirements files

## 📚 Reference Commands

```bash
# Install uv (in container)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Compile with hashes
uv pip compile --generate-hashes requirements.in --output-file requirements.txt

# Install from lock file
uv pip sync requirements.txt

# Check dependency tree
uv tree

# Update specific package
uv lock --upgrade-package requests

# Dry run updates
uv lock --upgrade --dry-run
