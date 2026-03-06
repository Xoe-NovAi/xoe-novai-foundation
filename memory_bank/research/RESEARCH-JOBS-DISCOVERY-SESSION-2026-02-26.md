# Additional Research Jobs - Post Discovery Session

**Date**: 2026-02-26  
**Source**: Discovery session for GitHub multi-account tools and automation

---

## Research Findings Summary

### Tools Discovered

| Tool | Type | Relevance | Status |
|------|------|-----------|--------|
| **gh-context** | CLI Extension | ✅ Direct replacement for custom scripts | Research |
| **gh-accounts** | CLI Tool | ✅ SSH key automation | Research |
| **ghswap** | NPM Package | ⚠️ JavaScript-based | Evaluate |
| **copilot-usage** | GitHub Action | ✅ Usage reports | Research |
| **copilot-api** | API Wrapper | ⚠️ OpenAI compatible | Evaluate |
| **austenstone/copilot-usage** | GitHub Action | ✅ Job summaries | Research |

---

## New Research Jobs

| Job ID | Title | Description | Priority | Suggested Tool |
|--------|-------|-------------|----------|---------------|
| RJ-025 | Evaluate gh-context for account switching | Test gh-context extension for faster account switching vs custom scripts | HIGH | gh-context |
| RJ-026 | Copilot Usage API Integration | Research integrating Copilot usage API into audit system | HIGH | GitHub API |
| RJ-027 | Automated Quota Alerts | Research/implement automated alerts when quota thresholds hit | MEDIUM | Custom + GitHub Actions |
| RJ-028 | Split Test Automation | Research tools to automate model comparison split tests | MEDIUM | Custom |
| RJ-029 | GitHub Actions Integration | Research using GitHub Actions for automated account management | LOW | GitHub Actions |

---

## Tool Evaluation Details

### gh-context (Recommended)

- **What**: GitHub CLI extension for multi-account switching
- **Features**: 
  - Quick account switching
  - Per-directory account mapping
  - Git config automation
- **Install**: `gh extension install naveenalok/gh-context`
- **Status**: ✅ Recommended for implementation

### copilot-usage (GitHub Action)

- **What**: Create Copilot usage reports as job summaries
- **Features**:
  - Usage tracking
  - Job summary integration
  - Organization-level reporting
- **Install**: GitHub Marketplace
- **Status**: ✅ Good for organization-level monitoring

### gh-accounts (CLI)

- **What**: Full account management with SSH automation
- **Features**:
  - SSH key creation/management
  - Git config automation
  - Interactive switching
- **Install**: Manual (Go binary)
- **Status**: ✅ Good for initial setup

---

## Recommendations

### Immediate Actions

1. **Test gh-context**: Install and evaluate vs current custom scripts
2. **Integrate Copilot Usage API**: Update audit script to pull Copilot-specific data
3. **Add GitHub Actions**: Use copilot-usage for organization-level tracking

### Future Enhancements

1. **Automation**: Set up automated quota alerts using GitHub Actions
2. **Dashboard**: Integrate usage data into existing dashboard
3. **Split Test**: Create automated split test runner

---

## Resources

- gh-context: https://github.com/naveenalok/gh-context
- gh-accounts: https://github.com/vishnutvm/gh-accounts
- copilot-usage: https://github.com/austenstone/copilot-usage
- copilot-api: https://github.com/ericc-ch/copilot-api
- GitHub Copilot Usage API: https://docs.github.com/en/copilot/managing-copilot/understanding-and-managing-copilot-usage

---

**Added**: 2026-02-26  
**Status**: Ready for assignment
