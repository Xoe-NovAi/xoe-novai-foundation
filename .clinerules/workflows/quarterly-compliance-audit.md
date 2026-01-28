# Quarterly Compliance Audit Workflow

**Purpose**: Comprehensive regulatory compliance validation and reporting
**Frequency**: Quarterly (every 3 months) - scheduled maintenance
**Trigger**: `/quarterly-compliance-audit.md [quarter] [year]`

**Why Workflow vs Chain**: Extensive documentation requirements, regulatory reporting, multi-system validation, executive reporting needs

---

## 1. Audit Preparation & Scoping

### **Audit Scope Definition**
- **Regulatory Requirements**: SOC2, GDPR, accessibility standards
- **System Coverage**: All production services and data handling
- **Time Period**: Previous quarter's operations and changes
- **Stakeholder Identification**: Teams and executives requiring reports

### **Resource Allocation**
```bash
# Create audit workspace
mkdir -p audits/quarterly-$(date +%Y)-Q$QUARTER
cd audits/quarterly-$(date +%Y)-Q$QUARTER

# Set up audit logging
exec > audit-log-$(date +%Y%m%d).txt 2>&1
echo "Quarterly Compliance Audit Started: $(date)"
echo "Quarter: Q$QUARTER $(date +%Y)"
echo "Auditor: Cline AI Assistant"
```

---

## 2. Security & Access Control Audit

### **Authentication & Authorization**
- **Access Logs Analysis**: Review login patterns and failed attempts
- **Role-Based Access**: Verify RBAC implementation and enforcement
- **Multi-Factor Authentication**: Confirm MFA requirements and usage
- **Session Management**: Validate session timeouts and security controls

### **Automated Security Assessment**
```bash
# Check authentication logs
grep "LOGIN\|AUTH" /var/log/auth.log | tail -100

# Verify MFA enforcement
curl -s http://localhost:8000/admin/security-status | jq '.mfa_enforced'

# Review access patterns
podman-compose logs auth-service | grep -E "(GRANT|DENY|LOGIN)" | tail -50

# Check for suspicious activity
grep "FAILED.*LOGIN" /var/log/security.log | wc -l
```

### **Findings Documentation**
- **Critical Issues**: Immediate remediation required
- **High Priority**: Fix within audit period
- **Medium Priority**: Address in next quarter
- **Recommendations**: Preventive measures for future

---

## 3. Data Protection & Privacy Compliance

### **GDPR Compliance Verification**
- **Data Processing Inventory**: Catalog all personal data handling
- **Consent Management**: Verify consent collection and storage
- **Data Subject Rights**: Test access, rectification, erasure procedures
- **Breach Notification**: Review incident response procedures

### **Data Protection Assessment**
```bash
# Check data encryption
openssl x509 -in ssl/cert.pem -text | grep -A 5 "Subject Alternative Name"

# Verify data retention policies
find data/ -type f -mtime +90 | wc -l  # Files older than 90 days

# Test data subject access
curl -X POST http://localhost:8000/gdpr/data-request \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "request_type": "access"}'

# Review consent logs
grep "CONSENT" application-logs/*.log | tail -20
```

---

## 4. System Reliability & Performance

### **Uptime & Availability Analysis**
- **Service Level Agreements**: Verify uptime against targets
- **Incident Review**: Analyze production incidents and responses
- **Backup Verification**: Confirm backup procedures and testing
- **Disaster Recovery**: Validate DR procedures and documentation

### **Performance Metrics Review**
```bash
# Check uptime statistics
curl -s http://localhost:9090/api/v1/query?query=uptime_ratio | jq '.data.result[0].value[1]'

# Review incident count
grep "INCIDENT\|ALERT" monitoring-logs/*.log | wc -l

# Verify backup success
ls -la backups/ | grep $(date +%Y%m) | head -5

# Test DR procedures
echo "DR test would be performed here - documented in runbook"
```

---

## 5. Accessibility & User Experience

### **WCAG 2.2 AA Compliance**
- **Automated Testing**: Run accessibility scanners
- **Manual Review**: Key user journeys and forms
- **Screen Reader Compatibility**: Verify assistive technology support
- **Color Contrast**: Validate visual accessibility standards

### **Accessibility Assessment**
```bash
# Run automated accessibility tests
npx axe-core http://localhost:3000 --stdout

# Check color contrast
npx color-contrast-checker --url http://localhost:3000

# Test keyboard navigation
# (Manual testing documented in accessibility-test-results.md)

# Validate semantic HTML
curl -s http://localhost:3000 | grep -c "<main>\|<nav>\|<header>"
```

---

## 6. Third-Party Risk Assessment

### **Vendor & Dependency Review**
- **Software Bill of Materials**: Complete dependency inventory
- **Security Vulnerabilities**: Scan for known vulnerabilities
- **License Compliance**: Verify open source license adherence
- **Update Status**: Review patch management procedures

### **Dependency Analysis**
```bash
# Generate SBOM
pip-licenses --format json > sbom-$(date +%Y%m%d).json

# Check for vulnerabilities
safety check --full-report > vulnerability-report-$(date +%Y%m%d).txt

# Review update status
pip list --outdated > outdated-packages-$(date +%Y%m%d).txt

# License compliance
pip-licenses | grep -E "(GPL|AGPL)" > gpl-licenses-$(date +%Y%m%d).txt
```

---

## 7. Audit Report Generation

### **Executive Summary**
```bash
# Generate executive summary
cat > executive-summary-Q$QUARTER-$(date +%Y).md << EOF
# Quarterly Compliance Audit Summary
## Q$QUARTER $(date +%Y)

### Overall Compliance Status: [COMPLIANT/NON-COMPLIANT]

### Key Findings:
- Security: [STATUS] - [BRIEF DESCRIPTION]
- Privacy: [STATUS] - [BRIEF DESCRIPTION]
- Reliability: [STATUS] - [BRIEF DESCRIPTION]
- Accessibility: [STATUS] - [BRIEF DESCRIPTION]
- Third-Party Risk: [STATUS] - [BRIEF DESCRIPTION]

### Critical Issues Requiring Attention:
1. [ISSUE 1]
2. [ISSUE 2]
3. [ISSUE 3]

### Recommendations for Next Quarter:
1. [RECOMMENDATION 1]
2. [RECOMMENDATION 2]
3. [RECOMMENDATION 3]

### Conclusion:
[Detailed conclusion and next steps]
EOF
```

### **Detailed Technical Report**
- **Methodology**: Audit procedures and tools used
- **Detailed Findings**: Technical details for each compliance area
- **Evidence**: Screenshots, logs, and test results
- **Remediation Plans**: Specific steps to address findings

### **Stakeholder Communication**
```xml
<ask_followup_question>
Audit complete. Executive summary generated. How would you like to distribute the findings?

**Distribution Options:**
- **Email Report**: Send detailed technical report to compliance team
- **Executive Briefing**: Schedule meeting to review executive summary
- **Team Presentation**: Present findings to development team
- **Documentation Only**: Add to compliance repository without distribution

Select distribution method:
["Email Report", "Executive Briefing", "Team Presentation", "Documentation Only", "Multiple Options"]
</ask_followup_question>
```

---

## 8. Remediation Planning & Tracking

### **Action Item Creation**
- **Critical Issues**: Immediate remediation with deadlines
- **High Priority**: Next sprint remediation
- **Medium Priority**: Next quarter remediation
- **Monitoring**: Ongoing compliance monitoring setup

### **Compliance Dashboard Updates**
```bash
# Update compliance metrics
echo "Q$QUARTER $(date +%Y) Compliance Status: $OVERALL_STATUS" >> compliance-dashboard.md
echo "- Security: $SECURITY_STATUS" >> compliance-dashboard.md
echo "- Privacy: $PRIVACY_STATUS" >> compliance-dashboard.md
echo "- Accessibility: $ACCESSIBILITY_STATUS" >> compliance-dashboard.md

# Schedule follow-up reviews
echo "Next Audit: $(date -d "+3 months" +%Y-%m-%d)" >> audit-schedule.md
```

---

## 9. Continuous Improvement

### **Process Enhancement**
- **Audit Efficiency**: Identify time-saving improvements
- **Automation Opportunities**: Areas for additional automated checking
- **Documentation Updates**: Improve procedures based on findings
- **Training Needs**: Skills development for compliance team

### **Memory Bank Updates**
```bash
# Update compliance tracking
echo "Quarterly Compliance Audit Q$QUARTER $(date +%Y): $OVERALL_STATUS" >> memory_bank/activeContext.md
echo "Key Findings: $CRITICAL_ISSUES critical, $HIGH_ISSUES high priority" >> memory_bank/activeContext.md

# Update progress tracking
echo "Compliance: Q$QUARTER audit completed with $OVERALL_STATUS status" >> memory_bank/progress.md
```

---

## Success Metrics
- ✅ **Completion Rate**: Audit completed within scheduled timeframe
- ✅ **Finding Quality**: All compliance areas thoroughly assessed
- ✅ **Remediation Planning**: Actionable remediation plans created
- ✅ **Stakeholder Satisfaction**: Reports meet executive and team needs
- ✅ **Process Improvement**: Identified enhancements for next audit

---

## Compliance Standards Reference
- **SOC2**: Security, availability, processing integrity, confidentiality, privacy
- **GDPR**: Data protection, consent management, breach notification, subject rights
- **WCAG 2.2 AA**: Perceivable, operable, understandable, robust accessibility
- **ISO 27001**: Information security management system requirements

---

## Audit Checklist
- [ ] Pre-audit preparation complete
- [ ] Security controls verified
- [ ] Privacy compliance confirmed
- [ ] System reliability validated
- [ ] Accessibility standards met
- [ ] Third-party risks assessed
- [ ] Executive report generated
- [ ] Remediation plans created
- [ ] Continuous improvement identified
- [ ] Follow-up audit scheduled

This workflow ensures comprehensive quarterly compliance validation with detailed reporting, actionable remediation plans, and continuous process improvement.
