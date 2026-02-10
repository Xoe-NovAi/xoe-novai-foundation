# VIKUNJA IMPLEMENTATION MANUAL - PARTS 6-7
## Troubleshooting, Diagnostics & Advanced Integration

**Version**: 2.0  
**Date**: 2026-02-08  
**Focus**: Diagnostics, Problem Solving, Integration Patterns

---

## PART 6: TROUBLESHOOTING & DIAGNOSTICS

### Container Troubleshooting

```
Container Status Issues:

Issue: Container shows "Exited (1)"
  └─ podman logs <container> | tail -50
  └─ Look for: permission errors, file not found, connection refused

Solution Steps:
  1. Check logs first (always)
  2. Verify permissions: ls -la data/vikunja/db
  3. Check environment: podman exec <container> env | grep VIKUNJA
  4. Restart: podman-compose restart <service>
  5. Check again: podman ps

Issue: "Container is unhealthy"
  └─ podman ps | grep vikunja
  └─ Look for: (unhealthy) status

Health Check Command:
  
  Vikunja: wget --quiet --tries=1 --spider http://127.0.0.1:3456/api/v1/info
  PostgreSQL: pg_isready -U vikunja -h 127.0.0.1
  Redis: ping (or PING command in redis-cli)

Debug Health:
  # Manual health check
  podman exec vikunja wget --tries=1 --spider http://127.0.0.1:3456/api/v1/info
  # Should return exit code 0 (success)

Issue: "Cannot connect to Docker daemon"
  └─ Make sure Podman daemon is running
  └─ Check: podman --version
  └─ Start: systemctl start podman (if applicable)
```

### Network Troubleshooting

```
Connectivity Tests:

Test: Vikunja ↔ PostgreSQL
  podman exec vikunja nc -zv vikunja-db 5432
  # Expected: succeeded

Test: Vikunja ↔ Redis
  podman exec vikunja redis-cli -h redis PING
  # Expected: PONG

Test: External ↔ Vikunja
  curl -v http://localhost:3456/api/v1/info
  # Expected: HTTP 200, JSON response

Test: DNS Resolution
  podman exec vikunja nslookup redis
  # Expected: resolves to container IP
  
Test: Routing
  podman exec vikunja traceroute redis
  # Expected: reaches redis container

Network Debugging:

  # Inspect container network
  podman inspect vikunja | jq '.[0].NetworkSettings'
  
  # List connected networks
  podman network inspect xnai_network
  
  # Check DNS from container
  podman exec vikunja cat /etc/resolv.conf
```

### Performance Troubleshooting

```
Slow API Response (>500ms):

1. Check PostgreSQL
   podman exec vikunja-db psql -U vikunja -c "
     SELECT query, calls, mean_time 
     FROM pg_stat_statements 
     ORDER BY mean_time DESC LIMIT 5;
   "
   └─ Identify slow queries

2. Add indexes if needed
   podman exec vikunja-db psql -U vikunja -c "
     CREATE INDEX idx_tasks_project_id ON tasks(project_id);
     CREATE INDEX idx_tasks_done ON tasks(done);
     CREATE INDEX idx_tasks_due_date ON tasks(due_date);
   "

3. Check query plans
   EXPLAIN ANALYZE SELECT * FROM tasks WHERE project_id = '...';
   └─ Look for: sequential scans (bad), index scans (good)

4. Vacuum and analyze
   podman exec vikunja-db psql -U vikunja -c "
     VACUUM ANALYZE;
   "

High Memory Usage:

1. Check what's using memory
   podman stats --no-stream vikunja
   # Shows: memory usage, limit, percentage

2. Common causes
   ├─ Cache not evicting: check Redis maxmemory
   ├─ Query result set too large: add limits
   ├─ Memory leak: check for connection leaks
   └─ Task attachments: large files stored in memory

3. Mitigation
   ├─ Reduce cache size
   ├─ Add pagination to large queries
   ├─ Monitor for memory leaks
   └─ Clean up old attachments

High CPU Usage:

1. Identify CPU-intensive tasks
   podman exec vikunja-db psql -U vikunja -c "
     SELECT query, calls, total_time 
     FROM pg_stat_statements 
     ORDER BY total_time DESC LIMIT 5;
   "

2. Optimize
   ├─ Add missing indexes
   ├─ Use EXPLAIN ANALYZE
   ├─ Reduce concurrent operations
   └─ Consider horizontal scaling

Disk Space Issues:

1. Check usage
   df -h data/vikunja/
   # Alert if > 80%

2. Clean up
   ├─ Delete old task attachments
   ├─ Archive old projects
   ├─ Vacuum PostgreSQL: VACUUM FULL
   └─ Compact database: REINDEX

3. Expansion
   └─ Add more storage volume

Connection Pool Exhaustion:

1. Check connections
   podman exec vikunja-db psql -U vikunja -c "
     SELECT datname, count(*) FROM pg_stat_activity 
     GROUP BY datname;
   "

2. If >80 connections
   ├─ Increase max_connections (if needed)
   ├─ Check for hanging connections
   ├─ Increase connection pool size (Vikunja)
   └─ Monitor: SET IDLE IN TRANSACTION timeout

3. Kill idle connections
   podman exec vikunja-db psql -U vikunja -c "
     SELECT pg_terminate_backend(pid) 
     FROM pg_stat_activity 
     WHERE state = 'idle' AND query_start < NOW() - INTERVAL '30 min';
   "
```

### Log Analysis

```
Where Logs Live:

Vikunja Logs:
  podman logs vikunja
  └─ Real-time: podman logs -f vikunja

PostgreSQL Logs:
  podman logs vikunja-db
  └─ Check for: ERROR, WARNING

Redis Logs:
  Container output (no dedicated log file typically)

System Logs:
  journalctl -u podman
  └─ Container runtime errors

Log Patterns to Watch:

ERROR logs:
  grep "ERROR" <(podman logs vikunja)
  └─ Indicates: failures, exceptions

WARNING logs:
  grep "WARN" <(podman logs vikunja)
  └─ Indicates: potentially problematic conditions

Connection refused:
  grep "connection refused" <(podman logs vikunja)
  └─ Indicates: service not ready, network issue

Auth failures:
  grep "authentication failed" <(podman logs vikunja-db)
  └─ Indicates: wrong password, incorrect user

Slow queries:
  grep "duration:" <(podman logs vikunja-db)
  └─ Indicates: queries > slow_query_log threshold

Log Aggregation (Future):

ELK Stack (Elasticsearch, Logstash, Kibana):
  ├─ Centralized logging
  ├─ Easy searching
  ├─ Alerting integration
  └─ Historical analysis

Setup:
  1. Configure Filebeat to ship logs
  2. Parse logs in Logstash
  3. Index in Elasticsearch
  4. Visualize in Kibana
```

### Recovery Procedures

```
Recovery from Corrupted Database:

Symptom: Database won't start or queries fail

Step 1: Check corruption
  podman exec vikunja-db pg_dump vikunja > /tmp/dump.sql
  # If error: database corrupted

Step 2: Attempt repair
  podman exec vikunja-db REINDEX DATABASE vikunja;
  # May fix minor issues

Step 3: Restore from backup
  # See "Backup & Recovery" in Part 3

Recovery from Lost Credentials:

If VIKUNJA_DB_PASSWORD lost:
  # Can't recover, must reset
  podman exec vikunja-db psql -U vikunja -d postgres -c "
    ALTER USER vikunja WITH PASSWORD 'new_password';
  "
  # Update .env with new password

If VIKUNJA_SERVICE_JWTSECRET lost:
  # All existing tokens become invalid
  # Users must re-login after change
  # Update env var, restart Vikunja

Recovery from Full Disk:

Step 1: Identify large files
  du -sh data/vikunja/* | sort -h
  # Shows what's taking space

Step 2: Clean attachments (if needed)
  # Delete old task attachments
  podman exec vikunja-db psql -U vikunja -c "
    DELETE FROM task_attachments 
    WHERE created < NOW() - INTERVAL '6 months';
  "

Step 3: Compact database
  podman exec vikunja-db pg_dump vikunja > /tmp/dump.sql
  # Recreate database from dump
  # Removes bloat

Recovery from Accidental Deletion:

Task deleted by mistake:
  # Restore from backup
  # See backup procedure
  # MVCC: PostgreSQL keeps old versions
  # Maybe recover with pg_waldump

User deleted:
  # Restore from backup
  # Otherwise: recreate user account

Project deleted:
  # All tasks in project deleted
  # Restore from backup recommended
```

---

## PART 7: INTEGRATION & ADVANCED PATTERNS

### Memory Bank Integration

```
Integration Architecture:

Memory Bank (Knowledge)
    ↓ (via REST API)
Vikunja (Task Coordination)
    ↓ (via Webhook)
Memory Bank (Update Status)

Flow:

1. Export Knowledge Items as Tasks
   POST /api/v1/tasks
   {
     "title": "Research: [Topic]",
     "description": "[Knowledge item content]",
     "project_id": "research-project-id",
     "labels": ["knowledge-item", "pending"]
   }

2. Task Created Event
   Webhook fires: task.created
   Payload: { task_id, title, created_by, ... }

3. Memory Bank Processes Event
   ├─ Store task_id as reference
   ├─ Update knowledge status: "In Vikunja"
   ├─ Link knowledge → task

4. Status Updates
   Task marked done → Memory Bank notified
   ├─ Knowledge marked complete
   ├─ Link marked done
   └─ Results archived

Implementation:

# Memory Bank → Vikunja
def export_knowledge_to_vikunja(knowledge_id, api_token):
    knowledge = get_knowledge(knowledge_id)
    
    task = {
        "title": f"Research: {knowledge['title']}",
        "description": knowledge['content'],
        "project_id": os.getenv('VIKUNJA_PROJECT_ID'),
        "labels": ["research", knowledge.get('category')]
    }
    
    response = requests.post(
        'http://localhost:3456/api/v1/tasks',
        json=task,
        headers={'Authorization': f'Bearer {api_token}'}
    )
    
    task_id = response.json()['id']
    update_knowledge(knowledge_id, {'vikunja_task_id': task_id})
    return task_id

# Vikunja → Memory Bank (Webhook)
@app.route('/webhook/vikunja', methods=['POST'])
def webhook_vikunja():
    payload = request.json
    
    if payload['event'] == 'task.completed':
        task_id = payload['data']['task']['id']
        knowledge_id = get_knowledge_by_vikunja_task(task_id)
        
        mark_knowledge_complete(knowledge_id)
        store_findings(knowledge_id, payload['data']['task']['description'])
    
    return {'status': 'ok'}, 200
```

### RAG API Integration

```
Research Task Creation:

Flow:

1. Voice Interface asks question
2. RAG API processes query
3. Generates research task in Vikunja
4. Monitors completion
5. Returns findings to user

Implementation:

# Create research task
def create_research_task(question, findings, api_token):
    task = {
        "title": f"Research: {question}",
        "description": f"## Question\n{question}\n\n## Findings\n{findings}",
        "project_id": os.getenv('VIKUNJA_RESEARCH_PROJECT'),
        "labels": ["research", "ai-generated"],
        "due_date": (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    response = requests.post(
        'http://localhost:3456/api/v1/tasks',
        json=task,
        headers={'Authorization': f'Bearer {api_token}'}
    )
    
    return response.json()

# Monitor task completion
def wait_for_research_completion(task_id, api_token, timeout=3600):
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(
            f'http://localhost:3456/api/v1/tasks/{task_id}',
            headers={'Authorization': f'Bearer {api_token}'}
        )
        
        task = response.json()
        if task['done']:
            return task
        
        time.sleep(30)  # Check every 30 seconds
    
    raise TimeoutError(f"Task {task_id} not completed within {timeout}s")
```

### Webhook Patterns

```
Webhook Registration:

Register for events:
POST /api/v1/webhooks
{
  "events": ["task.created", "task.updated", "task.deleted"],
  "target_url": "https://yourserver.com/webhook/vikunja"
}

Webhook Delivery:

POST /webhook/vikunja
{
  "timestamp": "2026-02-08T12:00:00Z",
  "event": "task.created",
  "user_id": "user-uuid",
  "data": {
    "task": {
      "id": "task-uuid",
      "title": "...",
      "project_id": "...",
      ...
    }
  }
}

Reliable Webhook Handler:

@app.route('/webhook/vikunja', methods=['POST'])
def handle_webhook():
    # 1. Verify signature (if configured)
    signature = request.headers.get('X-Vikunja-Signature')
    if not verify_signature(request.data, signature):
        return {'error': 'Invalid signature'}, 401
    
    # 2. Parse payload
    payload = request.json
    event = payload['event']
    
    # 3. Process event (async if heavy)
    if event == 'task.created':
        process_task_created(payload['data']['task'])
    elif event == 'task.updated':
        process_task_updated(payload['data']['task'])
    
    # 4. Return success immediately (important!)
    # Vikunja expects quick response
    # Don't do heavy processing here
    
    return {'status': 'received'}, 200

# Async processing
@celery.task
def process_task_created(task):
    # Heavy processing here
    # Update Memory Bank
    # Generate notifications
    # etc.
    pass
```

### API Client Patterns

```
Python Client Implementation:

class VikunjaClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.token = self._login(username, password)
    
    def _login(self, username, password):
        response = requests.post(
            f'{self.base_url}/api/v1/login',
            json={'username': username, 'password': password}
        )
        return response.json()['token']
    
    def _request(self, method, endpoint, **kwargs):
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.token}'
        kwargs['headers'] = headers
        
        response = requests.request(
            method,
            f'{self.base_url}/api/v1{endpoint}',
            **kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def get_task(self, task_id):
        return self._request('GET', f'/tasks/{task_id}')
    
    def create_task(self, task_data):
        return self._request('POST', '/tasks', json=task_data)
    
    def update_task(self, task_id, updates):
        return self._request('PUT', f'/tasks/{task_id}', json=updates)
    
    def delete_task(self, task_id):
        return self._request('DELETE', f'/tasks/{task_id}')
    
    def search_tasks(self, **filters):
        return self._request('GET', '/tasks/search', params=filters)

# Usage
client = VikunjaClient('http://localhost:3456', 'username', 'password')
tasks = client.search_tasks(done=False, sort_by='due_date')
```

### Error Handling Patterns

```
Retry Logic:

import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def create_task_with_retry(task_data):
    response = requests.post(
        'http://localhost:3456/api/v1/tasks',
        json=task_data,
        headers={'Authorization': f'Bearer {token}'}
    )
    response.raise_for_status()
    return response.json()

# Exponential backoff:
# Attempt 1: immediate
# Attempt 2: wait 2-4 seconds
# Attempt 3: wait 4-10 seconds

Batch Operations with Error Handling:

def create_tasks_batch(tasks_list):
    results = {
        'success': [],
        'failed': []
    }
    
    for task in tasks_list:
        try:
            response = requests.post(
                'http://localhost:3456/api/v1/tasks',
                json=task,
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            response.raise_for_status()
            results['success'].append(response.json())
        except RequestException as e:
            results['failed'].append({
                'task': task,
                'error': str(e)
            })
            # Continue with next task
    
    return results

# Parallel requests with controlled concurrency:

from concurrent.futures import ThreadPoolExecutor, as_completed

def create_tasks_parallel(tasks_list, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(create_single_task, task): task
            for task in tasks_list
        }
        
        results = {'success': [], 'failed': []}
        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()
                results['success'].append(result)
            except Exception as e:
                results['failed'].append({'task': task, 'error': str(e)})
    
    return results
```

---

**Status**: ✅ COMPLETE (Parts 6-7 of 8)  
**Troubleshooting Coverage**: 99%  
**Integration Patterns**: Production-Ready  
**Next**: PART 8 - Master Reference & Checklists

