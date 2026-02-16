# Security Trinity Validation Playbook

**For**: Xoe-NovAi Phase 13 - Security Stack Verification  
**Tools**: Syft (SBOM), Grype (CVE), Trivy (Secrets/Misconfig)  
**Compliance**: Supply chain tracking, vulnerability management, configuration security

---

## 🎯 Executive Summary

**Objective**: Validate that the Sovereign Security Trinity (Syft, Grype, Trivy) is operational and enforcing security policies for the XNAi stack.

**Success Criteria**:
- ✅ Syft generates complete SBOM for all containers
- ✅ Grype scans SBOM with no HIGH/CRITICAL unpatched CVEs
- ✅ Trivy scans configurations with no secrets exposed
- ✅ Security policy enforced (fail-on-high threshold)
- ✅ Compliance report generated for audit trail

**Duration**: 45 minutes (Phase 13)

---

## 🛡️ Tool 1: Syft - SBOM Generation

### Purpose
Generate Software Bill of Materials (SBOM) to track all components, dependencies, and licenses in the XNAi stack.

### Installation Verification
```bash
# Check Syft version
syft version

# Expected output:
# syft 1.x.x

# If not installed:
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
```

### Task 1.1: Generate SBOM for Project Directory
```bash
# Scan entire XNAi foundation directory
syft packages dir:/home/arcana-novai/Documents/xnai-foundation \
  --output json \
  > /logs/xnai-sbom.json

# Validate output
jq '.artifacts | length' /logs/xnai-sbom.json
# Should show 100+ packages (Python, Node, system libs)

# Check for critical components
jq '.artifacts[] | select(.name | contains("redis"))' /logs/xnai-sbom.json
jq '.artifacts[] | select(.name | contains("qdrant"))' /logs/xnai-sbom.json
jq '.artifacts[] | select(.name | contains("fastapi"))' /logs/xnai-sbom.json
```

### Task 1.2: Generate SBOM for Container Images
```bash
# RAG API container
syft packages docker:xnai-rag-api:latest \
  --output json \
  > /logs/sbom-rag-api.json

# Chainlit UI container
syft packages docker:xnai-ui:latest \
  --output json \
  > /logs/sbom-chainlit.json

# Crawler container
syft packages docker:xnai-crawler:latest \
  --output json \
  > /logs/sbom-crawler.json

# Curation worker
syft packages docker:xnai-curation-worker:latest \
  --output json \
  > /logs/sbom-curation-worker.json

# Redis (if custom image)
syft packages docker:redis:7.4.1 \
  --output json \
  > /logs/sbom-redis.json
```

### Task 1.3: Aggregate Stack SBOM
```python
# scripts/aggregate_sbom.py

import json
from collections import defaultdict

def aggregate_sboms(sbom_files: list) -> dict:
    """Combine multiple SBOMs into stack-wide inventory"""
    aggregated = {
        'metadata': {
            'stack': 'XNAi Foundation',
            'version': 'v0.1.4-stable',
            'generated': datetime.now().isoformat()
        },
        'components': defaultdict(list)
    }
    
    for sbom_file in sbom_files:
        with open(sbom_file, 'r') as f:
            sbom = json.load(f)
            
        for artifact in sbom.get('artifacts', []):
            key = f"{artifact['name']}@{artifact['version']}"
            aggregated['components'][key].append({
                'source': sbom_file,
                'type': artifact.get('type'),
                'language': artifact.get('language'),
                'licenses': artifact.get('licenses', [])
            })
    
    return dict(aggregated)

# Run aggregation
sbom_files = [
    '/logs/xnai-sbom.json',
    '/logs/sbom-rag-api.json',
    '/logs/sbom-chainlit.json',
    '/logs/sbom-crawler.json',
    '/logs/sbom-curation-worker.json'
]

aggregated = aggregate_sboms(sbom_files)

with open('/logs/xnai-stack-sbom.json', 'w') as f:
    json.dump(aggregated, f, indent=2)

print(f"✅ Stack SBOM: {len(aggregated['components'])} unique components")
```

### Task 1.4: License Compliance Check
```bash
# Extract licenses from SBOM
jq '.artifacts[] | .licenses[]' /logs/xnai-sbom.json | sort -u > /logs/licenses.txt

# Flag non-permissive licenses
grep -v -E '(MIT|Apache|BSD|ISC|Unlicense|CC0)' /logs/licenses.txt > /logs/licenses-flagged.txt

# Manual review required for flagged licenses
cat /logs/licenses-flagged.txt
```

**Success Criteria Task 1**:
- ✅ SBOM generated for all containers
- ✅ 100+ components tracked
- ✅ Critical dependencies present (Redis, FastAPI, Qdrant)
- ✅ License compliance verified

---

## 🔍 Tool 2: Grype - CVE Vulnerability Scanning

### Purpose
Scan SBOM for known CVEs (Common Vulnerabilities and Exposures) and enforce fail-on-high policy.

### Installation Verification
```bash
# Check Grype version
grype version

# Expected output:
# grype 0.x.x

# If not installed:
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
```

### Task 2.1: Scan SBOM for CVEs
```bash
# Scan stack SBOM
grype sbom:/logs/xnai-sbom.json \
  --fail-on high \
  --output json \
  > /logs/grype-scan-results.json

# If scan fails (HIGH/CRITICAL found), examine:
cat /logs/grype-scan-results.json | jq '.matches[] | select(.vulnerability.severity == "High" or .vulnerability.severity == "Critical")'
```

### Task 2.2: Analyze CVE Results
```python
# scripts/analyze_cves.py

import json

def analyze_cve_results(results_file: str) -> dict:
    """Analyze Grype CVE scan results"""
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    stats = {
        'total_vulns': len(results.get('matches', [])),
        'by_severity': {},
        'by_component': {},
        'actionable': []
    }
    
    for match in results.get('matches', []):
        severity = match['vulnerability']['severity']
        component = match['artifact']['name']
        cve_id = match['vulnerability']['id']
        
        # Count by severity
        stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
        
        # Count by component
        if component not in stats['by_component']:
            stats['by_component'][component] = []
        stats['by_component'][component].append({
            'cve': cve_id,
            'severity': severity,
            'fixed_in': match['vulnerability'].get('fix', {}).get('versions', [])
        })
        
        # Flag actionable (has fix available)
        if match['vulnerability'].get('fix', {}).get('state') == 'fixed':
            stats['actionable'].append({
                'component': component,
                'cve': cve_id,
                'severity': severity,
                'current_version': match['artifact']['version'],
                'fixed_version': match['vulnerability']['fix']['versions'][0]
            })
    
    return stats

# Run analysis
stats = analyze_cve_results('/logs/grype-scan-results.json')

print(f"Total vulnerabilities: {stats['total_vulns']}")
print(f"By severity: {stats['by_severity']}")
print(f"Actionable fixes: {len(stats['actionable'])}")

# Save report
with open('/logs/cve-analysis-report.json', 'w') as f:
    json.dump(stats, f, indent=2)
```

### Task 2.3: CVE Remediation Plan
```markdown
# /logs/cve-remediation-plan.md

## HIGH/CRITICAL CVEs Requiring Action

### CVE-2024-XXXXX (CRITICAL)
- **Component**: redis-py 4.5.1
- **Severity**: CRITICAL (CVSS 9.8)
- **Description**: Remote code execution via malformed command
- **Fix**: Upgrade to redis-py 5.0.0+
- **Action**: Update requirements.txt, rebuild containers
- **Timeline**: Immediate (P0)

### CVE-2024-YYYYY (HIGH)
- **Component**: requests 2.28.0
- **Severity**: HIGH (CVSS 7.5)
- **Description**: Server-Side Request Forgery (SSRF)
- **Fix**: Upgrade to requests 2.31.0+
- **Action**: Update requirements.txt, test compatibility
- **Timeline**: Within 7 days (P1)

## MEDIUM/LOW CVEs - Monitor

[List of non-critical CVEs with upgrade recommendations]
```

### Task 2.4: Automated CVE Scanning (CI/CD)
```yaml
# .github/workflows/security-scan.yml

name: Security Scan (Grype)

on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  cve-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          path: .
          format: json
          output-file: sbom.json
      
      - name: Scan for CVEs
        uses: anchore/scan-action@v3
        with:
          sbom: sbom.json
          fail-build: true
          severity-cutoff: high
      
      - name: Upload results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
```

**Success Criteria Task 2**:
- ✅ Grype scan completes without errors
- ✅ Zero HIGH/CRITICAL unpatched CVEs
- ✅ Remediation plan created for flagged issues
- ✅ CI/CD pipeline configured for continuous scanning

---

## 🔐 Tool 3: Trivy - Secrets & Misconfiguration Scanning

### Purpose
Scan codebase and configurations for exposed secrets, hardcoded credentials, and misconfigurations.

### Installation Verification
```bash
# Check Trivy version
trivy version

# Expected output:
# trivy 0.x.x

# If not installed:
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

### Task 3.1: Configuration Scan
```bash
# Scan entire project for misconfigurations
trivy config /home/arcana-novai/Documents/xnai-foundation \
  --severity HIGH,CRITICAL \
  --format json \
  --output /logs/trivy-config-scan.json

# Check for findings
jq '.Results[] | select(.Misconfigurations | length > 0)' /logs/trivy-config-scan.json
```

### Task 3.2: Secrets Detection
```bash
# Scan for exposed secrets
trivy fs /home/arcana-novai/Documents/xnai-foundation \
  --scanners secret \
  --severity HIGH,CRITICAL \
  --format json \
  --output /logs/trivy-secrets-scan.json

# Flag critical secrets
jq '.Results[] | select(.Secrets | length > 0) | .Secrets[] | select(.Severity == "CRITICAL" or .Severity == "HIGH")' /logs/trivy-secrets-scan.json > /logs/secrets-flagged.json

# Review flagged secrets
cat /logs/secrets-flagged.json
```

**Common Findings to Check**:
| Check | Expected | Validation |
|-------|----------|------------|
| .env file committed | ❌ No | `.gitignore` includes `.env` |
| API keys in code | ❌ No | `git grep -i "api_key"` |
| Passwords hardcoded | ❌ No | `git grep -i "password"` |
| Private keys | ❌ No | `find . -name "*.pem" -o -name "*.key"` |
| AWS credentials | ❌ No | `.aws/` not in repo |

### Task 3.3: Docker Configuration Audit
```bash
# Scan docker-compose.yml
trivy config docker-compose.yml \
  --severity HIGH,CRITICAL

# Common issues to check:
# - Containers running as root
# - Exposed ports without necessity
# - Missing resource limits
# - Using :latest tags (not pinned)
# - Environment variables with secrets
```

**Expected Trivy Checks**:
```
✅ PASS: Containers run as non-root (UID 1001)
✅ PASS: Read-only filesystems where applicable
✅ PASS: Resource limits defined (memory, CPU)
✅ PASS: Networks properly isolated
✅ PASS: No secrets in environment variables
❌ FAIL: Fix any HIGH/CRITICAL findings
```

### Task 3.4: Policy Enforcement
Create `/configs/trivy-policy.rego`:
```rego
# Trivy policy for XNAi stack (OPA Rego)

package xnai.security

deny[msg] {
  input.kind == "Secret"
  msg := "Hardcoded secrets detected in configuration"
}

deny[msg] {
  input.kind == "ConfigMap"
  contains(input.data, "password")
  msg := "Password found in ConfigMap - use Secrets instead"
}

deny[msg] {
  input.kind == "Container"
  input.securityContext.runAsUser == 0
  msg := "Container running as root - must use non-root user"
}

deny[msg] {
  input.kind == "Container"
  not input.resources.limits
  msg := "Container missing resource limits"
}
```

Apply policy:
```bash
trivy config /home/arcana-novai/Documents/xnai-foundation \
  --policy /configs/trivy-policy.rego \
  --severity HIGH,CRITICAL
```

**Success Criteria Task 3**:
- ✅ Zero secrets exposed in repository
- ✅ Zero HIGH/CRITICAL misconfigurations
- ✅ All containers non-root (UID 1001)
- ✅ Resource limits defined
- ✅ Policy enforcement active

---

## 📊 Phase 13 Compliance Report

### Task 4.1: Generate Compliance Report
```python
# scripts/generate_compliance_report.py

import json
from datetime import datetime

def generate_compliance_report(
    sbom_file: str,
    cve_file: str,
    trivy_config_file: str,
    trivy_secrets_file: str
) -> dict:
    """Generate comprehensive security compliance report"""
    
    report = {
        'metadata': {
            'stack': 'XNAi Foundation',
            'version': 'v0.1.4-stable',
            'scan_date': datetime.now().isoformat(),
            'compliance_status': 'PASS'  # Updated if issues found
        },
        'sbom': {
            'status': 'COMPLETE',
            'components_tracked': 0,
            'licenses_flagged': 0
        },
        'cve_scan': {
            'status': 'PASS',
            'total_vulns': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        },
        'secrets_scan': {
            'status': 'PASS',
            'secrets_found': 0,
            'critical_secrets': 0
        },
        'config_scan': {
            'status': 'PASS',
            'misconfigurations': 0,
            'critical_issues': 0
        },
        'recommendations': []
    }
    
    # Parse SBOM
    with open(sbom_file, 'r') as f:
        sbom = json.load(f)
    report['sbom']['components_tracked'] = len(sbom.get('artifacts', []))
    
    # Parse CVE results
    with open(cve_file, 'r') as f:
        cves = json.load(f)
    
    for match in cves.get('matches', []):
        severity = match['vulnerability']['severity']
        report['cve_scan']['total_vulns'] += 1
        report['cve_scan'][severity.lower()] = report['cve_scan'].get(severity.lower(), 0) + 1
    
    if report['cve_scan']['critical'] > 0 or report['cve_scan']['high'] > 0:
        report['cve_scan']['status'] = 'FAIL'
        report['metadata']['compliance_status'] = 'FAIL'
        report['recommendations'].append(
            f"Address {report['cve_scan']['critical']} CRITICAL and {report['cve_scan']['high']} HIGH CVEs immediately"
        )
    
    # Parse Trivy secrets
    with open(trivy_secrets_file, 'r') as f:
        secrets = json.load(f)
    
    for result in secrets.get('Results', []):
        for secret in result.get('Secrets', []):
            report['secrets_scan']['secrets_found'] += 1
            if secret['Severity'] in ['CRITICAL', 'HIGH']:
                report['secrets_scan']['critical_secrets'] += 1
    
    if report['secrets_scan']['critical_secrets'] > 0:
        report['secrets_scan']['status'] = 'FAIL'
        report['metadata']['compliance_status'] = 'FAIL'
        report['recommendations'].append(
            f"Remove {report['secrets_scan']['critical_secrets']} exposed secrets from repository"
        )
    
    # Parse Trivy config
    with open(trivy_config_file, 'r') as f:
        config = json.load(f)
    
    for result in config.get('Results', []):
        for misc in result.get('Misconfigurations', []):
            report['config_scan']['misconfigurations'] += 1
            if misc['Severity'] in ['CRITICAL', 'HIGH']:
                report['config_scan']['critical_issues'] += 1
    
    if report['config_scan']['critical_issues'] > 0:
        report['config_scan']['status'] = 'FAIL'
        report['metadata']['compliance_status'] = 'FAIL'
        report['recommendations'].append(
            f"Fix {report['config_scan']['critical_issues']} critical configuration issues"
        )
    
    return report

# Generate report
report = generate_compliance_report(
    '/logs/xnai-sbom.json',
    '/logs/grype-scan-results.json',
    '/logs/trivy-config-scan.json',
    '/logs/trivy-secrets-scan.json'
)

# Save report
with open('/logs/security-compliance-report.json', 'w') as f:
    json.dump(report, f, indent=2)

# Print summary
print(f"🛡️ Security Compliance Report")
print(f"Status: {report['metadata']['compliance_status']}")
print(f"Components tracked: {report['sbom']['components_tracked']}")
print(f"CVEs: {report['cve_scan']['total_vulns']} ({report['cve_scan']['critical']} critical)")
print(f"Secrets: {report['secrets_scan']['secrets_found']} ({report['secrets_scan']['critical_secrets']} critical)")
print(f"Misconfigurations: {report['config_scan']['misconfigurations']} ({report['config_scan']['critical_issues']} critical)")

if report['metadata']['compliance_status'] == 'FAIL':
    print("\n⚠️ COMPLIANCE FAILED - ACTION REQUIRED:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
    sys.exit(1)
else:
    print("\n✅ COMPLIANCE PASSED - Stack is secure")
    sys.exit(0)
```

### Task 4.2: Markdown Report for Documentation
```bash
# Generate human-readable report
python3 << 'EOF'
import json

with open('/logs/security-compliance-report.json', 'r') as f:
    report = json.load(f)

md_report = f"""# XNAi Security Compliance Report

**Generated**: {report['metadata']['scan_date']}  
**Stack Version**: {report['metadata']['version']}  
**Compliance Status**: {report['metadata']['compliance_status']}

## Summary

| Component | Status | Details |
|-----------|--------|---------|
| SBOM Generation | {report['sbom']['status']} | {report['sbom']['components_tracked']} components tracked |
| CVE Scanning | {report['cve_scan']['status']} | {report['cve_scan']['total_vulns']} vulnerabilities ({report['cve_scan']['critical']} critical) |
| Secrets Detection | {report['secrets_scan']['status']} | {report['secrets_scan']['secrets_found']} secrets ({report['secrets_scan']['critical_secrets']} critical) |
| Configuration Audit | {report['config_scan']['status']} | {report['config_scan']['misconfigurations']} issues ({report['config_scan']['critical_issues']} critical) |

## CVE Breakdown

- **CRITICAL**: {report['cve_scan']['critical']}
- **HIGH**: {report['cve_scan']['high']}
- **MEDIUM**: {report['cve_scan']['medium']}
- **LOW**: {report['cve_scan']['low']}

## Recommendations

"""

for rec in report['recommendations']:
    md_report += f"- {rec}\n"

md_report += f"""

## Next Steps

{'✅ No action required - stack is compliant' if report['metadata']['compliance_status'] == 'PASS' else '⚠️ Address flagged issues before production deployment'}
"""

with open('/logs/security-compliance-report.md', 'w') as f:
    f.write(md_report)

print("✅ Markdown report saved to /logs/security-compliance-report.md")
EOF
```

---

## ✅ Phase 13 Success Validation

### Validation Checklist
| Task | Expected | Validation Command |
|------|----------|-------------------|
| Syft installed | ✅ | `syft version` |
| Grype installed | ✅ | `grype version` |
| Trivy installed | ✅ | `trivy version` |
| SBOM generated | ✅ | `ls -lh /logs/xnai-sbom.json` |
| CVE scan complete | ✅ | `ls -lh /logs/grype-scan-results.json` |
| Secrets scan complete | ✅ | `ls -lh /logs/trivy-secrets-scan.json` |
| Config scan complete | ✅ | `ls -lh /logs/trivy-config-scan.json` |
| Compliance report generated | ✅ | `cat /logs/security-compliance-report.md` |
| Status: PASS | ✅ | `jq '.metadata.compliance_status' /logs/security-compliance-report.json` |

### Final Validation Script
```bash
# scripts/validate_security_trinity.sh

#!/bin/bash
set -e

echo "🛡️ Validating Sovereign Security Trinity..."

# Check tools
echo "1. Checking tool installations..."
syft version > /dev/null && echo "  ✅ Syft installed" || exit 1
grype version > /dev/null && echo "  ✅ Grype installed" || exit 1
trivy version > /dev/null && echo "  ✅ Trivy installed" || exit 1

# Check outputs
echo "2. Checking scan outputs..."
test -f /logs/xnai-sbom.json && echo "  ✅ SBOM generated" || exit 1
test -f /logs/grype-scan-results.json && echo "  ✅ CVE scan complete" || exit 1
test -f /logs/trivy-secrets-scan.json && echo "  ✅ Secrets scan complete" || exit 1
test -f /logs/trivy-config-scan.json && echo "  ✅ Config scan complete" || exit 1

# Check compliance status
echo "3. Checking compliance status..."
STATUS=$(jq -r '.metadata.compliance_status' /logs/security-compliance-report.json)
if [ "$STATUS" = "PASS" ]; then
  echo "  ✅ Compliance: PASS"
  echo ""
  echo "🎉 Security Trinity validation successful!"
  exit 0
else
  echo "  ❌ Compliance: FAIL"
  echo ""
  echo "⚠️ Review /logs/security-compliance-report.md for details"
  exit 1
fi
```

---

## 📚 References

- Syft generates SBOM in JSON format with artifacts, metadata, and relationships for software components
- Grype scans SBOM for CVEs with severity levels and fail-on-high enforcement capability
- Trivy scans for secrets, misconfigurations, and vulnerabilities in containers and configurations
- Redis stores ACL passwords hashed with SHA256; security scans should not find plaintext credentials

---

**Status**: Ready for Phase 13 Execution  
**Duration**: 45 minutes  
**Priority**: P1 (security validation)  
**Deliverables**: Compliance report, remediation plan, validated security posture
