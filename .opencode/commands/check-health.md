# Check Health Command

## Purpose
Verify all Foundation stack services are running and healthy.

## Usage
```
/check-health
```

## Services Checked

| Service | Endpoint | Check |
|---------|----------|-------|
| RAG API | localhost:8000/health | HTTP 200 |
| Agent Bus | localhost:6379 | PING |
| Consul | localhost:8500/v1/status/leader | HTTP 200 |
| Vikunja | localhost:3456/api/v1/info | HTTP 200 |

## Workflow
1. Check each service endpoint
2. Record response times
3. Identify failures
4. Report overall health

## Output
```
## Health Check Report

### Services Status
| Service | Status | Latency |
|---------|--------|---------|
| RAG API | ✅ UP | 45ms |
| Agent Bus | ✅ UP | 2ms |
| Consul | ✅ UP | 12ms |
| Vikunja | ❌ DOWN | - |

### Issues
- Vikunja: Connection refused

### Recommendations
1. Start Vikunja: podman start vikunja
2. Check logs: podman logs vikunja

### Overall Health: DEGRADED
3/4 services healthy
```

## Commands Executed
```bash
curl -s http://localhost:8000/health
redis-cli -h localhost -p 6379 ping
curl -s http://localhost:8500/v1/status/leader
curl -s http://localhost:3456/api/v1/info
```
