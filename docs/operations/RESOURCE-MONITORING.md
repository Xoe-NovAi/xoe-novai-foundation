# 📊 Resource Monitoring & Administration

The Omega Stack uses a combination of autonomous sentinels and manual overrides to manage hardware resources on 6.6GB RAM host environments.

---

## 🛡️ 1. Stack Sentinel (Autonomous Admin)

The **Sentinel** is a background monitor that watches system health and takes administrative action to prevent Out-of-Memory (OOM) crashes.

### Main Tasks
1. **Telemetry Broadcasting**: Sends real-time RAM/CPU/Swap stats to the Agent Bus (`xnai:agent_bus`).
2. **OOM Mitigation**: If free RAM drops below 2GB, it automatically stops non-essential services (like the Crawler).
3. **Swap/zRAM Monitoring**: Watches for high swap pressure and triggers remediation.

### Control
```bash
# Start the Sentinel prototype
python3 scripts/sentinel_prototype.py
```

---

## 🧛 2. Vampire Control (Timer Management)

**Vampire Control** manages "vampire" services—background systemd timers that consume bandwidth and CPU during idle periods. 

### Why Use It?
When running deep LLM inference or large-scale library curation, every byte of bandwidth and cycle of CPU counts. Vampire Control allows you to "purge" these background tasks with a single command.

### Managed Timers
- `xnai-github-audit.timer`
- `xnai-quota-audit.timer`
- `runtime-probe.timer`
- `xnai-antigravity-monitor.timer`

### Usage
| Command | Action |
|:---|:---|
| `scripts/vampire_control.sh status` | Check if vampire timers are active. |
| `scripts/vampire_control.sh stop` | **Vampire Purge**: Disable and stop all background timers. |
| `scripts/vampire_control.sh start` | Restore background monitoring. |

---

## 🛠️ 3. Monitoring Baseline (6.6GB Host)

| Metric | Normal | Warning | Critical |
|:---|:---|:---|:---|
| **Physical RAM** | 3-4 GB | >5.5 GB | >6.0 GB |
| **zRAM Usage** | <2 GB | >6 GB | >10 GB |
| **CPU Load** | <50% | >80% | >95% |

---
*Document sealed by Gemini General. The Hearth is monitored. 🔱*
