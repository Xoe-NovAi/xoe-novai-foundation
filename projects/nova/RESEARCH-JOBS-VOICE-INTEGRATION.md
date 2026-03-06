# Research Jobs Queue - Voice App Integration

## Status
**Last Updated**: 2026-02-22
**Total Jobs**: 8 (2 P0-Critical, 3 P1-High, 3 P2-Medium)

---

## P0-CRITICAL (2 jobs)

### JOB-VOICE-001: Original vs XNAi-Enhanced Comparison Study
| Aspect | Details |
|--------|---------|
| **Priority** | P0-CRITICAL |
| **Description** | Compare the original Claude Code CLI built voice app with the XNAi-enhanced version |
| **Tasks** | - Identify original Claude Code CLI version files (pre-XNAi integration) |
|  | - Compare architecture differences |
|  | - Document what XNAi tools added to the voice app |
|  | - Identify which XNAi features were integrated and how |
|  | - Measure improvement in functionality |
| **Deliverables** | - Side-by-side architecture comparison |
|  | - Feature enhancement matrix |
|  | - Integration value assessment |
| **Estimated Effort** | 1 day |
| **Dependencies** | Access to original Claude Code CLI version |

### JOB-VOICE-002: XNAi → Nova Integration Feasibility
| Aspect | Details |
|--------|---------|
| **Priority** | P0-CRITICAL |
| **Description** | Determine which XNAi Foundation features can be integrated into Nova voice app |
| **Tasks** | - Analyze Qdrant integration potential for Nova memory |
|  | - Assess Agent Bus coordination for voice app |
|  | - Evaluate Consul service discovery benefits |
|  | - Document Knowledge Absorption System applicability |
|  | - Identify Chainlit infrastructure layer reuse |
| **Deliverables** | - Integration feasibility matrix |
|  | - Effort estimates per component |
|  | - Recommended integration path |
| **Estimated Effort** | 2 days |
| **Dependencies** | None |

---

## P1-HIGH (3 jobs)

### JOB-VOICE-003: Nova → XNAi Feature Extraction
| Aspect | Details |
|--------|---------|
| **Priority** | P1-HIGH |
| **Description** | Extract reusable components from Nova for XNAi Foundation |
| **Tasks** | - Extract Memory Bank system (SQLite + semantic search) |
|  | - Extract CLI Abstraction factory pattern |
|  | - Extract Circuit Breaker pattern from health_monitor.py |
|  | - Extract MCP Server implementation |
|  | - Document extraction requirements |
| **Deliverables** | - Extracted component modules |
|  | - Integration documentation |
|  | - Test cases |
| **Estimated Effort** | 3 days |
| **Dependencies** | JOB-VOICE-002 |

### JOB-VOICE-004: Standalone Tool Packaging
| Aspect | Details |
|--------|---------|
| **Priority** | P1-HIGH |
| **Description** | Package Nova components as standalone community tools |
| **Tasks** | - Package AudioGuardian as standalone Mac tool |
|  | - Package Bluetooth Audio Router |
|  | - Package Memory Bank as pip-installable |
|  | - Package Wake Word Detector |
|  | - Create documentation and examples |
| **Deliverables** | - 4 standalone Python packages |
|  | - PyPI-ready packages |
|  | - Documentation and examples |
| **Estimated Effort** | 1 week |
| **Dependencies** | JOB-VOICE-003 |

### JOB-VOICE-005: Cross-Platform Audio Abstraction
| Aspect | Details |
|--------|---------|
| **Priority** | P1-HIGH |
| **Description** | Create platform abstraction for audio device management |
| **Tasks** | - Design abstract AudioDeviceManager interface |
|  | - Implement macOS CoreAudio backend |
|  | - Implement Linux PulseAudio backend |
|  | - Implement Windows Core Audio backend |
|  | - Create unified API |
| **Deliverables** | - Platform abstraction layer |
|  | - 3 platform implementations |
|  | - Test suite |
| **Estimated Effort** | 2 weeks |
| **Dependencies** | None |

---

## P2-MEDIUM (3 jobs)

### JOB-VOICE-006: Accessibility Enhancement Research
| Aspect | Details |
|--------|---------|
| **Priority** | P2-MEDIUM |
| **Description** | Research accessibility enhancements for voice apps |
| **Tasks** | - Document blind user workflow patterns |
|  | - Research screen reader integration |
|  | - Analyze voice feedback best practices |
|  | - Research hands-free coding patterns |
|  | - Document accessibility testing methods |
| **Deliverables** | - Accessibility guidelines document |
|  | - Testing checklist |
|  | - User experience recommendations |
| **Estimated Effort** | 3 days |
| **Dependencies** | None |

### JOB-VOICE-007: Voice App Performance Benchmarking
| Aspect | Details |
|--------|---------|
| **Priority** | P2-MEDIUM |
| **Description** | Benchmark Nova voice app performance |
| **Tasks** | - Measure STT latency (Whisper faster-whisper) |
|  | - Measure TTS latency (Kokoro) |
|  | - Measure LLM response time (Ollama) |
|  | - Measure memory footprint |
|  | - Compare with XNAi Foundation metrics |
| **Deliverables** | - Performance benchmark report |
|  | - Optimization recommendations |
|  | - Comparison with XNAi |
| **Estimated Effort** | 2 days |
| **Dependencies** | None |

### JOB-VOICE-008: Voice App Security Audit
| Aspect | Details |
|--------|---------|
| **Priority** | P2-MEDIUM |
| **Description** | Security audit of Nova voice app |
| **Tasks** | - Audit audio input handling |
|  | - Review configuration file security |
|  | - Analyze network communication |
|  | - Check for credential exposure |
|  | - Document security best practices |
| **Deliverables** | - Security audit report |
|  | - Remediation recommendations |
|  | - Security hardening guide |
| **Estimated Effort** | 3 days |
| **Dependencies** | None |

---

## Knowledge Gaps Requiring Research

### Gap-KG-001: Original Claude Code CLI Version
**Question**: Where is the original Claude Code CLI built voice app version before XNAi integration?
**Action**: Locate and preserve original version for comparison study
**Priority**: P0-CRITICAL

### Gap-KG-002: Windows Audio API Compatibility
**Question**: What Windows audio APIs are compatible with Nova's patterns?
**Action**: Research Windows Core Audio API and WASAPI
**Priority**: P1-HIGH

### Gap-KG-003: Linux Bluetooth Audio
**Question**: How to implement AirPods detection on Linux (BlueZ)?
**Action**: Research BlueZ D-Bus API for Bluetooth device detection
**Priority**: P1-HIGH

### Gap-KG-004: Memory System Comparison
**Question**: How does Nova's SQLite memory compare to XNAi's Qdrant?
**Action**: Benchmark and compare memory systems
**Priority**: P2-MEDIUM

---

## Completed Jobs

None yet - all jobs are pending.

---

## Notes

1. Voice app research is NEW TRACK alongside XNAi Foundation work
2. These jobs can run in parallel with Chainlit consolidation
3. Comparison study (JOB-VOICE-001) requires original version access
4. Standalone tool packaging can proceed independently

---

**Owner**: MC-Overseer Agent
**Review Frequency**: Weekly
**Related**: `projects/nova/PROJECT-DISTINCTION-XNAI-NOVA.md`