# Evaluation Criteria — Wave 5 Manual Split Test

**Date**: 2026-02-26  
**Purpose**: Score and compare Wave 5 manuals from Raptor, Haiku, and MiniMax

---

## Scoring Overview

| Metric | Weight | Max Score |
|--------|--------|-----------|
| Completeness | 25% | 5 |
| Technical Accuracy | 25% | 5 |
| Actionability | 20% | 5 |
| Token Efficiency | 15% | 5 |
| Structure & Navigation | 15% | 5 |
| **TOTAL** | **100%** | **5** |

---

## Detailed Rubric

### 1. Completeness (25%)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | All 5 phases fully documented with implementation, testing, troubleshooting |
| 4 | Good | All 5 phases covered, minor gaps in optional sections |
| 3 | Acceptable | 4 phases complete, 1 partially covered |
| 2 | Poor | 3 phases covered, significant gaps |
| 1 | Fail | Less than 3 phases covered |

**Checklist**:
- [ ] Phase 5A: Session Management
- [ ] Phase 5B: Agent Bus
- [ ] Phase 5C: IAM v2.0
- [ ] Phase 5D: Vikunja Integration
- [ ] Phase 5E: E5 Onboarding
- [ ] Quick Reference Card

---

### 2. Technical Accuracy (25%)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | All file paths valid, percentages accurate, no technical errors |
| 4 | Good | 90% accurate, minor discrepancies |
| 3 | Acceptable | 75% accurate, some outdated information |
| 2 | Poor | 50% accurate, significant errors |
| 1 | Fail | Less than 50% accurate, major hallucinations |

**Validation Points**:
- [ ] Phase completion percentages match (5A:60%, 5B:90%, 5C:85%, 5D:85%, 5E:80%)
- [ ] File paths exist and are correct
- [ ] RQ items correctly identified
- [ ] Account configuration accurate
- [ ] Technical terminology correct

---

### 3. Actionability (20%)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Copy-paste ready, clear steps, testable criteria |
| 4 | Good | Mostly actionable, minor ambiguity |
| 3 | Acceptable | Basic instructions, some unclear steps |
| 2 | Poor | Vague instructions, hard to follow |
| 1 | Fail | Not actionable, theoretical only |

**Checklist**:
- [ ] Step-by-step implementation guides
- [ ] Acceptance criteria are testable
- [ ] Code blocks are complete
- [ ] Commands are executable
- [ ] Troubleshooting covers common issues

---

### 4. Token Efficiency (15%)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | High information density, minimal redundancy |
| 4 | Good | Efficient, some repetition |
| 3 | Acceptable | Average efficiency |
| 2 | Poor | High redundancy, low information density |
| 1 | Fail | Excessive padding, low value |

**Measurement**:
- Information per token ratio
- Unique content vs. filler
- Table efficiency
- Code comment balance

---

### 5. Structure & Navigation (15%)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Clear TOC, logical flow, easy navigation |
| 4 | Good | Well organized, minor navigation issues |
| 3 | Acceptable | Basic structure, some confusion |
| 2 | Poor | Disorganized, hard to navigate |
| 1 | Fail | No clear structure |

**Checklist**:
- [ ] Table of Contents present
- [ ] Clear section headings
- [ ] Cross-references between sections
- [ ] Index or quick reference
- [ ] Consistent formatting

---

## Final Scoring

### Score Calculation

```
Final Score = (Completeness × 0.25) + (Accuracy × 0.25) + (Actionability × 0.20) + (Efficiency × 0.15) + (Structure × 0.15)
```

### Rating Thresholds

| Score | Rating |
|-------|--------|
| 4.5 - 5.0 | 🏆 Excellent |
| 4.0 - 4.4 | ✅ Good |
| 3.0 - 3.9 | ⚠️ Acceptable |
| 2.0 - 2.9 | ❌ Poor |
| < 2.0 | 💀 Fail |

---

## Comparison Matrix

| Criterion | Raptor | Haiku | MiniMax | kat-coder-pro |
|-----------|--------|-------|---------|---------------|
| Completeness | /5 | /5 | /5 | /5 |
| Accuracy | /5 | /5 | /5 | /5 |
| Actionability | /5 | /5 | /5 | /5 |
| Efficiency | /5 | /5 | /5 | /5 |
| Structure | /5 | /5 | /5 | /5 |
| **TOTAL** | /5 | /5 | /5 | /5 |

---

## Winner Determination

**Primary Winner**: Highest total score

**Category Winners**:
- 🏆 Best Completeness
- 🎯 Best Accuracy
- 🚀 Best Actionability
- 💰 Best Efficiency
- 📚 Best Structure

---

**Last Updated**: 2026-02-26  
**Test ID**: `WAVE-5-MANUAL-SPLIT-TEST-2026-02-26`
