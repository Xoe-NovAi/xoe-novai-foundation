# Team Onboarding Automation Workflow

**Purpose**: Streamlined new team member setup and integration
**Frequency**: Per new hire (varies) - triggered by HR/onboarding events
**Trigger**: `/team-onboarding.md [name] [role] [start-date]`

**Why Workflow vs Chain**: Multi-system setup, human coordination required, personalized configuration, extensive documentation needs

---

## 1. Pre-Onboarding Preparation

### **New Hire Information Gathering**
- **Basic Information**: Name, role, start date, manager, team
- **System Access Requirements**: Determine required accounts and permissions
- **Equipment Needs**: Hardware, software, and tool requirements
- **Security Clearances**: Background check status and access levels

### **Resource Preparation**
```bash
# Create user workspace
NEW_USER=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
mkdir -p onboarding/$NEW_USER-$(date +%Y%m%d)
cd onboarding/$NEW_USER-$(date +%Y%m%d)

# Initialize onboarding log
cat > onboarding-log.md << EOF
# Onboarding Log: $NAME
**Role**: $ROLE
**Start Date**: $START_DATE
**Onboarding Started**: $(date)
**Onboarding Lead**: Cline AI Assistant

## Progress Tracking
- [ ] Accounts Created
- [ ] Equipment Setup
- [ ] Development Environment
- [ ] Security Training
- [ ] Team Integration
- [ ] Documentation Complete
EOF
```

---

## 2. Account & Access Provisioning

### **Identity Management Setup**
- **Email Account**: Create company email and distribution lists
- **Single Sign-On**: Set up SSO access with appropriate roles
- **Directory Services**: Add to Active Directory/LDAP groups
- **Password Management**: Initialize secure password and MFA setup

### **Development Tool Access**
```bash
# Git repository access
curl -X POST http://localhost:8080/api/v1/repos/add-collaborator \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{\"username\": \"$NEW_USER\", \"permission\": \"write\"}"

# CI/CD pipeline access
kubectl create rolebinding $NEW_USER-developer \
  --clusterrole=developer \
  --user=$NEW_USER \
  --namespace=development

# Cloud platform access
aws iam create-user --user-name $NEW_USER
aws iam attach-user-policy --user-name $NEW_USER --policy-arn arn:aws:iam::aws:policy/DeveloperAccess
```

### **Communication Tools**
- **Slack/Teams**: Add to team channels and create welcome message
- **Project Management**: Add to Jira/Linear boards
- **Documentation**: Grant access to internal wiki and knowledge base
- **Calendar**: Set up team meetings and recurring events

---

## 3. Development Environment Setup

### **Local Environment Configuration**
- **Operating System**: Verify compatible OS version and updates
- **Development Tools**: Install IDE, version control, build tools
- **Security Software**: Endpoint protection, VPN, access management
- **Productivity Tools**: Communication, documentation, project management

### **Container & Development Setup**
```bash
# Clone development environment
git clone https://github.com/Xoe-NovAi/dev-environment.git $HOME/dev-env
cd $HOME/dev-env

# Set up local containers
podman-compose up -d redis postgres

# Configure development certificates
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=$NEW_USER.dev.local"

# Initialize project workspace
mkdir -p $HOME/projects/xoe-novai
git clone https://github.com/Xoe-NovAi/Xoe-NovAi.git $HOME/projects/xoe-novai
```

### **IDE and Tool Configuration**
```bash
# VS Code/Codium setup
code --install-extension ms-vscode.vscode-json
code --install-extension ms-vscode.vscode-python
code --install-extension ms-vscode.vscode-docker
code --install-extension codelldb  # For debugging

# Python environment
python3 -m venv $HOME/.venv/xoe-novai
source $HOME/.venv/xoe-novai/bin/activate
pip install -r $HOME/projects/xoe-novai/requirements-dev.txt

# Git configuration
git config --global user.name "$NAME"
git config --global user.email "$NEW_USER@company.com"
```

---

## 4. Security & Compliance Training

### **Security Awareness**
- **Password Policies**: Review and acknowledge password requirements
- **Data Handling**: Understand data classification and handling procedures
- **Incident Reporting**: Learn incident response and reporting procedures
- **Remote Access**: Configure VPN and secure remote access

### **Compliance Requirements**
```bash
# Review and acknowledge policies
echo "Security policies reviewed and acknowledged: $(date)" >> security-training.log

# Complete mandatory training modules
curl -X POST http://localhost:3001/api/training/complete \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$NEW_USER\", \"module\": \"security-basics\", \"completed\": true}"

# Set up security monitoring
curl -X POST http://localhost:8080/api/webhooks \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{\"url\": \"https://security.company.com/webhook\", \"events\": [\"security-alert\"]}"
```

### **Access Control Verification**
- **Least Privilege**: Confirm minimal required access granted
- **Just-in-Time Access**: Set up temporary elevated permissions for initial setup
- **Audit Logging**: Enable comprehensive access logging
- **Regular Reviews**: Schedule quarterly access reviews

---

## 5. Team Integration & Knowledge Transfer

### **Team Communication Setup**
```bash
# Slack/Teams integration
curl -X POST https://slack.com/api/users.admin.invite \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -d "email=$NEW_USER@company.com&channels=C1234567890,D9876543210"

# Welcome message
curl -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -d "channel=C1234567890&text=Welcome $NAME to the team! 🎉"

# Calendar invites
# (Integration with Google Calendar/Microsoft Outlook for team meetings)
```

### **Knowledge Base Access**
- **Documentation**: Grant access to all team documentation
- **Code Repositories**: Provide read access to relevant repositories
- **Runbooks**: Access to operational procedures and troubleshooting guides
- **Architecture Diagrams**: Access to system architecture and design documents

### **Mentorship Assignment**
```xml
<ask_followup_question>
New team member setup is progressing well. Who should be assigned as $NAME's primary mentor?

**Mentorship Options:**
- **Team Lead**: Direct manager for technical leadership
- **Senior Developer**: Peer mentor for day-to-day development guidance
- **DevOps Engineer**: Focus on infrastructure and deployment knowledge
- **Product Manager**: Emphasis on product vision and user needs
- **Multiple Mentors**: Combination approach with different focuses

Select primary mentorship approach:
["Team Lead", "Senior Developer", "DevOps Engineer", "Product Manager", "Multiple Mentors"]
</ask_followup_question>
```

---

## 6. Project Assignment & First Tasks

### **Initial Project Setup**
- **Repository Access**: Grant appropriate repository permissions
- **Issue Assignment**: Assign first development tasks or bugs
- **Code Review Setup**: Configure code review workflows
- **Testing Environment**: Set up access to testing and staging environments

### **Development Workflow Introduction**
```bash
# Set up first development task
gh issue create \
  --title "Welcome Task: $NAME's First Contribution" \
  --body "Complete your first contribution by fixing a small bug or adding a simple feature. This will help you get familiar with our development workflow." \
  --assignee "$NEW_USER"

# Create development branch
git checkout -b feature/$NEW_USER-welcome-task
git push -u origin feature/$NEW_USER-welcome-task

# Set up CI/CD for new branch
curl -X POST http://localhost:8080/api/v1/repos/hooks \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{\"active\": true, \"events\": [\"push\"], \"config\": {\"url\": \"http://jenkins.company.com/github-webhook/\"}}"
```

---

## 7. Equipment & Workspace Setup

### **Hardware Provisioning**
- **Laptop/Desktop**: Verify delivery and basic setup
- **Peripherals**: Monitor, keyboard, mouse, docking station
- **Mobile Devices**: Company phone, tablet if required
- **Accessories**: Security keys, VPN tokens, company swag

### **Workspace Configuration**
```bash
# Desktop environment setup
curl -X POST http://localhost:3002/api/desktop/setup \
  -H "Content-Type: application/json" \
  -d "{\"user\": \"$NEW_USER\", \"role\": \"$ROLE\", \"preferences\": {\"theme\": \"dark\", \"layout\": \"developer\"}}"

# Application installation
curl -X POST http://localhost:3002/api/software/install \
  -d "packages[]=vscode&packages[]=docker&packages[]=slack&packages[]=zoom"

# Network and security configuration
curl -X POST http://localhost:3002/api/network/setup \
  -d "user=$NEW_USER&vpn=true&firewall=true&updates=auto"
```

---

## 8. Onboarding Completion & Handover

### **Progress Verification**
```bash
# Run onboarding checklist verification
curl -X GET http://localhost:3003/api/onboarding/checklist/$NEW_USER

# Verify all systems accessible
curl -X POST http://localhost:3003/api/onboarding/verify \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$NEW_USER\", \"check_type\": \"full-access\"}"

# Generate completion report
cat > onboarding-complete-$(date +%Y%m%d).md << EOF
# Onboarding Complete: $NAME
**Completed**: $(date)
**Systems Verified**: All access confirmed
**Mentor Assigned**: $MENTOR_NAME
**First Task**: $FIRST_TASK_URL

## Access Confirmed:
- [x] Email and communication tools
- [x] Development environment
- [x] Code repositories
- [x] CI/CD pipelines
- [x] Testing environments
- [x] Documentation systems

## Next Steps:
1. Complete first development task
2. Attend team standup meeting
3. Schedule 1:1 with mentor
4. Review company policies and procedures

Welcome to the team! 🚀
EOF
```

### **Team Introduction**
```xml
<ask_followup_question>
Onboarding setup is complete! How would you like to introduce $NAME to the team?

**Introduction Options:**
- **Team Meeting**: Schedule a brief introduction during next standup
- **Slack Announcement**: Post a welcome message in team channels
- **Email Introduction**: Send a formal introduction email to the team
- **Personal Introduction**: Have their manager introduce them individually
- **Multiple Approaches**: Combination of announcement and meeting

Select introduction method:
["Team Meeting", "Slack Announcement", "Email Introduction", "Personal Introduction", "Multiple Approaches"]
</ask_followup_question>
```

---

## 9. Follow-up & Support

### **30-Day Check-in Planning**
- **Week 1**: Daily check-ins with mentor and manager
- **Week 2**: Bi-weekly check-ins, focus on integration
- **Month 1**: Monthly check-ins, performance and growth discussion
- **Ongoing**: Regular feedback and development discussions

### **Support Resources**
```bash
# Create support documentation
cat > $NEW_USER-support.md << EOF
# Support Resources for $NAME

## Key Contacts:
- **Manager**: $MANAGER_NAME - $MANAGER_EMAIL
- **Mentor**: $MENTOR_NAME - $MENTOR_EMAIL
- **HR Contact**: $HR_CONTACT - $HR_EMAIL
- **IT Support**: it-support@company.com

## Important Links:
- **Company Handbook**: https://handbook.company.com
- **Development Guidelines**: https://docs.company.com/development
- **Security Policies**: https://docs.company.com/security
- **Benefits Information**: https://hr.company.com/benefits

## Emergency Contacts:
- **IT Emergency**: Call 911 (or local equivalent)
- **Security Incident**: security@company.com
- **HR Emergency**: hr-emergency@company.com
EOF
```

### **Memory Bank Updates**
```bash
# Update team tracking
echo "New Team Member: $NAME ($ROLE) onboarded $(date)" >> memory_bank/activeContext.md
echo "Mentor: $MENTOR_NAME | Manager: $MANAGER_NAME" >> memory_bank/activeContext.md

# Update progress tracking
echo "Onboarding: $NAME successfully onboarded with full system access" >> memory_bank/progress.md
```

---

## Success Metrics
- ✅ **Setup Completion**: All accounts and access provisioned within 24 hours
- ✅ **Environment Readiness**: Development environment fully functional
- ✅ **Security Compliance**: All security training and access controls completed
- ✅ **Team Integration**: Successful introduction and mentorship assignment
- ✅ **First Contribution**: Completed initial development task within first week

---

## Onboarding Checklist
- [ ] Pre-onboarding information gathered
- [ ] Accounts and access provisioned
- [ ] Development environment configured
- [ ] Security training completed
- [ ] Team communication tools set up
- [ ] Equipment and workspace ready
- [ ] Project access and first tasks assigned
- [ ] Mentorship and support structure established
- [ ] Introduction to team completed
- [ ] Follow-up plan documented

---

## Emergency Procedures
**If onboarding is interrupted:**
1. Document current progress in onboarding log
2. Notify manager and HR of interruption
3. Preserve any partially created accounts
4. Schedule continuation session
5. Verify no security exposures created

This workflow ensures comprehensive, consistent, and efficient new team member onboarding with proper security, access controls, and team integration.
