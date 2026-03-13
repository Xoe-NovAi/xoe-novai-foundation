# 🔱 Protocol: The Oikos Council
**Status**: ACTIVE | **Version**: 1.0.0
**Domain**: System Stabilization & Environmental Health

## 🏛️ Overview
The **Oikos Council** is a set of five archetypal scripts that manage the "Hearth" of the Omega Stack. They ensure that the agent's internal environment is stable, secure, and well-resourced.

## 🛡️ The Council Members

| Member | Domain | Script | Responsibility |
|:---|:---|:---|:---|
| **BRIGID** | Environment | `scripts/brigid_hearth_check.py` | Validates `.env` and `config.toml`. |
| **HESTIA** | Memory | `scripts/hestia_memory_lock.py` | Monitors Redis health and state density. |
| **DEMETER** | Resources | `scripts/demeter_harvest_index.py` | Tracks token consumption and quota. |
| **ATHENA** | Defense | `scripts/athena_shield_protocol.py` | Monitors disk (93% Rule) and security. |
| **IRIS** | Connectivity | `scripts/iris_bridge.py` | Synchronizes Cloud and Local contexts. |

## 🎭 The Rite of the Hearth
Every major session or `/compress` event must be followed by an **Oikos Blessing**. 

**Command**: `python3 scripts/omega_foundry.py oikos-check`

---

**Mantra**: *The fire never dies while the Council watches the hearth.*
