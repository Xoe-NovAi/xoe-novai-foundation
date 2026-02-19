# Production Incident Response Workflow

**Purpose**: Automated incident handling and escalation for production issues
**Frequency**: Rare (<1/month) but critical when triggered
**Trigger**: `/production-incident-response.md [severity] [description]`

**Why Workflow vs Chain**: Complex decision trees, human judgment required, documentation critical

---

## 1. Incident Assessment & Triage

### **Gather Incident Information**
- **Severity Assessment**: Critical/High/Medium/Low based on user input
- **Impact Analysis**: Determine affected systems and users
- **Timeline**: Record incident start time and detection method
- **Initial Response**: Acknowledge incident and begin containment

### **Automated Data Collection**
```bash
# Collect system metrics
curl -s http://localhost:9090/api/v1/query?query=up | jq .

# Check application health
curl -f http://localhost:8000/health || echo "API health check failed"

# Gather recent logs
podman-compose logs --tail=100 > incident-logs-$(date +%Y%m%d-%H%M%S).log
```

---

## 2. Containment Actions

### **Automatic Containment (Based on Severity)**
**Critical Severity:**
- Execute emergency backup of critical data
- Scale down non-essential services
- Enable circuit breakers for external calls
- Notify on-call team immediately

**High Severity:**
- Create incident ticket in tracking system
- Enable enhanced monitoring and alerting
- Prepare rollback procedures
- Notify development team lead

**Medium/Low Severity:**
- Log incident for post-mortem analysis
- Monitor for escalation
- Continue normal operations

### **Service Isolation**
```bash
# Isolate affected services
podman-compose stop affected-service

# Enable maintenance mode
curl -X POST http://localhost:8000/admin/maintenance-mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "enabled", "message": "Incident response in progress"}'
```

---

## 3. Investigation & Diagnosis

### **Automated Diagnostic Collection**
- **Error Log Analysis**: Parse recent logs for patterns
- **Performance Metrics**: Check system resources and throughput
- **Dependency Health**: Verify database, cache, and external services
- **Recent Changes**: Review recent deployments and configuration changes

### **Intelligent Analysis**
```bash
# Analyze error patterns
grep "ERROR\|CRITICAL\|FATAL" incident-logs-*.log | head -20

# Check system resources
ps aux --sort=-%cpu | head -10
free -h
df -h

# Verify service dependencies
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## 4. Recovery Options Assessment

### **Rollback Feasibility Check**
- **Database Changes**: Check for schema modifications
- **Data Loss Risk**: Assess impact of reverting changes
- **Downtime Requirements**: Estimate rollback duration
- **Alternative Solutions**: Identify workarounds if rollback not feasible

### **Recovery Strategy Selection**
**Option A: Immediate Rollback**
- Revert to last known good state
- Minimal data loss but service interruption required

**Option B: Hotfix Deployment**
- Deploy emergency fix without full rollback
- Maintains service availability but requires code changes

**Option C: Mitigation & Monitoring**
- Implement temporary workarounds
- Enhanced monitoring to prevent escalation
- Schedule proper fix for next maintenance window

---

## 5. Execution & Escalation

### **Decision Point: Recovery Strategy**
```xml
<ask_followup_question>
Based on incident analysis, here are the recommended recovery options:

**Option A: Immediate Rollback**
- Risk: 15-minute downtime
- Data Loss: Minimal (last 5 minutes)
- Confidence: High (tested procedure)

**Option B: Emergency Hotfix**
- Risk: 5-minute deployment window
- Data Loss: None
- Confidence: Medium (requires code review)

**Option C: Temporary Mitigation**
- Risk: Continued degraded performance
- Data Loss: None
- Confidence: High (monitoring-based)

Which recovery strategy should I execute?
["Option A: Immediate Rollback", "Option B: Emergency Hotfix", "Option C: Temporary Mitigation", "Custom Approach"]
</ask_followup_question>
```

### **Strategy Execution**
**If Option A (Rollback):**
```bash
# Execute rollback procedure
./scripts/emergency-rollback.sh

# Verify rollback success
curl -f http://localhost:8000/health
podman-compose ps
```

**If Option B (Hotfix):**
```bash
# Deploy hotfix
podman-compose build --no-cache hotfix-service
podman-compose up -d hotfix-service

# Verify deployment
curl -f http://localhost:8000/health
```

**If Option C (Mitigation):**
```bash
# Enable enhanced monitoring
curl -X POST http://localhost:9090/-/reload

# Implement rate limiting
iptables -A INPUT -p tcp --dport 80 -m limit --limit 10/minute -j ACCEPT
```

---

## 6. Communication & Documentation

### **Stakeholder Notification**
- **Internal Team**: Slack notification with incident details
- **Management**: Executive summary if severity >= High
- **Customers**: Status page update if user-facing impact
- **External Partners**: Notification if integrations affected

### **Incident Documentation**
```bash
# Create incident report
cat > incident-report-$(date +%Y%m%d-%H%M%S).md << EOF
# Incident Report: $(date)

## Summary
- **Severity**: $SEVERITY
- **Detection**: $DETECTION_METHOD
- **Duration**: $DURATION
- **Impact**: $IMPACT_DESCRIPTION

## Timeline
- **Detected**: $(date)
- **Acknowledged**: $(date)
- **Resolved**: TBD

## Root Cause
TBD - To be determined in post-mortem

## Resolution
$RESOLUTION_APPLIED

## Prevention
TBD - Recommendations from post-mortem
EOF
```

---

## 7. Post-Incident Activities

### **Verification & Testing**
- **Health Checks**: Confirm all systems operational
- **Data Integrity**: Verify no data corruption occurred
- **Performance Validation**: Ensure normal operation restored
- **Monitoring**: Confirm alerts silenced appropriately

### **Follow-up Actions**
- **Post-Mortem Meeting**: Schedule within 24 hours
- **Documentation Updates**: Update runbooks with lessons learned
- **Monitoring Improvements**: Implement additional alerting if needed
- **Team Training**: Review incident response procedures

### **Memory Bank Updates**
```bash
# Update incident tracking
echo "Production incident resolved: $(date) - Severity: $SEVERITY" >> memory_bank/activeContext.md

# Update progress tracking
echo "Incident Response: Successful resolution of $SEVERITY incident" >> memory_bank/progress.md
```

---

## Success Metrics
- ✅ **MTTR**: Time to resolution within SLA targets
- ✅ **Communication**: All stakeholders informed appropriately
- ✅ **Documentation**: Complete incident report generated
- ✅ **Learning**: Actionable improvements identified
- ✅ **Prevention**: Monitoring enhancements implemented

---

## Emergency Contacts & Escalation
- **On-Call Engineer**: Primary incident responder
- **DevOps Lead**: Escalation for infrastructure issues
- **Security Team**: Escalation for security incidents
- **Executive Team**: Escalation for business-critical issues

This workflow ensures consistent, documented, and effective incident response while maintaining system stability and stakeholder communication.
