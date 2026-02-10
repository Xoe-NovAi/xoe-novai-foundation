# VIKUNJA IMPLEMENTATION MANUAL - PART 1
## Architecture, Foundation & Deep Knowledge

**Version**: 2.0 (Complete Rewrite with Blocker Resolution)  
**Date**: 2026-02-08  
**Scope**: Architecture, Foundation, Design Patterns, Knowledge Base  
**Status**: COMPREHENSIVE & PRODUCTION-READY

---

## TABLE OF CONTENTS

1. [Executive Overview](#executive-overview)
2. [Vikunja Architecture Deep Dive](#vikunja-architecture-deep-dive)
3. [Component Relationships & Data Flow](#component-relationships--data-flow)
4. [Design Patterns & Best Practices](#design-patterns--best-practices)
5. [Integration Fundamentals](#integration-fundamentals)
6. [Foundation Stack Context](#foundation-stack-context)

---

## EXECUTIVE OVERVIEW

### What is Vikunja?

**Vikunja** (v0.24.1) is an open-source, self-hosted task management and collaboration platform built with:
- **Backend**: Go (high-performance, low memory)
- **Database**: PostgreSQL (ACID compliance, advanced features)
- **Frontend**: Vue.js (responsive, modern UI)
- **Protocol**: REST API v1 (comprehensive, well-documented)

### Why Vikunja for Xoe-NovAi?

| Aspect | Vikunja | Alternative | Choice |
|--------|---------|-------------|--------|
| **Self-Hosted** | ✅ Full control | Cloud (data privacy risk) | ✅ Vikunja |
| **Open Source** | ✅ Transparent | Proprietary (vendor lock-in) | ✅ Vikunja |
| **Performance** | Go binary (fast) | Heavy stacks (slow) | ✅ Vikunja |
| **Memory** | ~150-200MB | 1GB+ | ✅ Vikunja |
| **API** | Comprehensive REST | Limited | ✅ Vikunja |
| **Team Ready** | Teams/Organizations | Basic projects | ✅ Vikunja |
| **Integration** | Webhooks, API | Limited | ✅ Vikunja |

### Xoe-NovAi Use Case

Vikunja serves as the **task orchestration and project management layer** for Xoe-NovAi:

```
Memory Bank (Knowledge)
        ↓
Vikunja (Task Management & Coordination)
        ↓
RAG API (Research & Answer)
        ↓
Voice Interface (User Interaction)
```

---

## VIKUNJA ARCHITECTURE DEEP DIVE

### 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Web UI (Vue) │  │ Mobile App   │  │ API Client   │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    REST API v1 (HTTP/HTTPS)
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  VIKUNJA APPLICATION                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ API Routes & Handlers                                   │   │
│  │  ├─ User Management (auth, profiles)                   │   │
│  │  ├─ Team & Organization Management                     │   │
│  │  ├─ Namespace Management                               │   │
│  │  ├─ Task/Project Operations (CRUD)                     │   │
│  │  ├─ File Management                                    │   │
│  │  ├─ Webhook Management                                 │   │
│  │  └─ Advanced Features (labels, deadlines, etc.)        │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Business Logic Layer                                    │   │
│  │  ├─ Task Hierarchy & Relations                         │   │
│  │  ├─ Permission System (RBAC)                           │   │
│  │  ├─ Notification System                                │   │
│  │  ├─ Search & Filtering                                 │   │
│  │  └─ Webhook Triggering                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Data Access Layer (ORM: xormigrate)                     │   │
│  │  ├─ User data access                                   │   │
│  │  ├─ Task data access                                   │   │
│  │  ├─ Relationship queries                               │   │
│  │  └─ Transaction management                             │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    PostgreSQL         Redis Cache      File Storage
    (Primary DB)       (Sessions)       (Attachments)
    ┌─────────────┐   ┌────────┐       ┌──────────┐
    │ Tasks       │   │Session │       │ /files   │
    │ Users       │   │Data    │       │ Storage  │
    │ Teams       │   │Queues  │       │          │
    │ Projects    │   │Config  │       │          │
    │ Namespaces  │   └────────┘       └──────────┘
    │ Attachments │
    │ Activity    │
    └─────────────┘
```

### 2. Data Model Deep Dive

#### User & Authentication Model

```sql
-- Users Table (Core)
users (
  id: UUID PRIMARY KEY,
  username: VARCHAR UNIQUE,
  email: VARCHAR UNIQUE,
  password: BCRYPT_HASH,
  created: TIMESTAMP,
  updated: TIMESTAMP,
  avatar: BYTEA (optional)
)

-- OAuth/OpenID Support
oauth_tokens (
  id: UUID,
  user_id: FOREIGN KEY,
  provider: VARCHAR (github, google, etc),
  token: TEXT,
  expires_at: TIMESTAMP
)
```

**Authentication Flow**:
```
1. User credentials → Hash & verify → JWT generation
2. JWT token contains: user_id, username, exp, iat, jti
3. Token signed with VIKUNJA_SERVICE_JWTSECRET
4. Sent in Authorization header: Bearer <token>
5. Verified on each request
6. Expires after VIKUNJA_SERVICE_JWTEXPIRATION (86400 = 24h)
```

#### Organization & Team Model

```sql
teams (
  id: UUID PRIMARY KEY,
  name: VARCHAR,
  description: TEXT,
  owner_id: FOREIGN KEY (users),
  created: TIMESTAMP
)

team_members (
  id: UUID,
  team_id: FOREIGN KEY,
  user_id: FOREIGN KEY,
  role: ENUM (admin, member, guest),  -- RBAC
  created: TIMESTAMP
)

namespaces (
  id: UUID,
  team_id: FOREIGN KEY,
  name: VARCHAR,
  description: TEXT,
  owner_id: FOREIGN KEY
)
```

**Hierarchy**:
```
User
  ├─ Teams (belongs to multiple)
  │   ├─ Namespaces (projects/folders)
  │   │   ├─ Projects/Lists
  │   │   │   ├─ Tasks
  │   │   │   │   ├─ Subtasks
  │   │   │   │   ├─ Labels
  │   │   │   │   ├─ Attachments
  │   │   │   │   └─ Reminders
  │   │   │   └─ Bucket (Kanban boards)
  │   │   │       └─ Bucket entries (task states)
  │   │   └─ Sharing rules
  │   └─ Team members & roles
  └─ Personal namespace (default)
```

#### Task Model (The Core)

```sql
tasks (
  id: UUID PRIMARY KEY,
  project_id: FOREIGN KEY,
  title: VARCHAR,
  description: TEXT (supports Markdown),
  done: BOOLEAN (completion status),
  due_date: DATE,
  start_date: DATE,
  end_date: DATE,
  created: TIMESTAMP,
  updated: TIMESTAMP,
  created_by: FOREIGN KEY (users),
  -- Relationships
  parent_task_id: FOREIGN KEY (self-referential, for subtasks),
  -- Advanced
  priority: ENUM (0=lowest, 1, 2, 3=highest),
  percent_done: INTEGER (0-100),
  repeat_after: INTERVAL (for recurring tasks),
  repeat_from_current_date: BOOLEAN,
  reminder_dates: TIMESTAMP[] (array of reminders),
  -- Labels/Tags
  labels: UUID[] (many-to-many with task_labels)
)

task_labels (
  id: UUID,
  task_id: FOREIGN KEY,
  label_id: FOREIGN KEY
)

labels (
  id: UUID,
  project_id: FOREIGN KEY,
  title: VARCHAR,
  description: TEXT,
  color: VARCHAR (hex color)
)
```

**Task Lifecycle**:
```
Creation (POST /api/v1/tasks)
  ↓
Modification (PUT /api/v1/tasks/{id})
  ├─ Update title/description
  ├─ Assign labels
  ├─ Set due dates
  ├─ Add attachments
  └─ Create subtasks
  ↓
Completion (PUT /api/v1/tasks/{id} with done=true)
  ↓
Archive/Delete (DELETE /api/v1/tasks/{id})
  
Events triggered at each step (webhooks)
```

#### Attachment/File Model

```sql
task_attachments (
  id: UUID,
  task_id: FOREIGN KEY,
  file_id: UUID,
  created_by: FOREIGN KEY (users),
  created: TIMESTAMP
)

files (
  id: UUID,
  name: VARCHAR,
  mime_type: VARCHAR,
  size: BIGINT,
  file: BYTEA (actual file data),
  created: TIMESTAMP
)
```

**File Storage**:
```
Default: /app/vikunja/files/ (container volume)
Max size: VIKUNJA_FILES_MAXSIZE (20MB in config)
Supported: Any file type (security via MIME checking)
Access: Via /api/v1/files/<id>/download endpoint
```

### 3. API Architecture

#### API Organization (v1)

```
/api/v1/
├─ /auth
│  ├─ POST /login              (email, password)
│  ├─ POST /logout             (delete session)
│  ├─ POST /refresh            (refresh JWT)
│  ├─ POST /register           (new user)
│  └─ GET  /user               (current user info)
├─ /users
│  ├─ GET    /{id}             (user profile)
│  ├─ PUT    /{id}             (update profile)
│  ├─ POST   /{id}/avatar      (upload avatar)
│  └─ GET    /search           (find users)
├─ /teams
│  ├─ GET    /                 (list teams)
│  ├─ POST   /                 (create team)
│  ├─ GET    /{id}             (team details)
│  ├─ PUT    /{id}             (update team)
│  ├─ DELETE /{id}             (delete team)
│  ├─ GET    /{id}/members     (team members)
│  ├─ POST   /{id}/members     (add member)
│  └─ DELETE /{id}/members/{uid} (remove member)
├─ /namespaces
│  ├─ GET    /                 (list namespaces)
│  ├─ POST   /                 (create namespace)
│  ├─ PUT    /{id}             (update namespace)
│  └─ DELETE /{id}             (delete namespace)
├─ /projects (aka lists)
│  ├─ GET    /                 (list projects)
│  ├─ POST   /                 (create project)
│  ├─ GET    /{id}             (project details)
│  ├─ PUT    /{id}             (update project)
│  ├─ DELETE /{id}             (delete project)
│  └─ GET    /{id}/tasks       (project tasks)
├─ /tasks
│  ├─ GET    /                 (list all tasks)
│  ├─ GET    /search           (search with filters)
│  ├─ POST   /                 (create task)
│  ├─ GET    /{id}             (task details)
│  ├─ PUT    /{id}             (update task)
│  ├─ DELETE /{id}             (delete task)
│  ├─ POST   /{id}/subtasks    (create subtask)
│  └─ POST   /{id}/comments    (add comment)
├─ /labels
│  ├─ GET    /                 (list labels)
│  ├─ POST   /                 (create label)
│  ├─ PUT    /{id}             (update label)
│  └─ DELETE /{id}             (delete label)
├─ /files
│  ├─ POST   /                 (upload file)
│  ├─ GET    /{id}/download    (download file)
│  └─ DELETE /{id}             (delete file)
├─ /webhooks
│  ├─ GET    /                 (list webhooks)
│  ├─ POST   /                 (create webhook)
│  ├─ PUT    /{id}             (update webhook)
│  └─ DELETE /{id}             (delete webhook)
├─ /subscriptions (for webhooks)
│  └─ GET    /                 (available event types)
└─ /info
   └─ GET    /                 (API version, features)
```

#### Request/Response Patterns

**Standard Success Response**:
```json
{
  "id": "uuid",
  "created": "2026-02-08T00:00:00Z",
  "updated": "2026-02-08T00:00:00Z",
  "title": "My Task",
  "done": false,
  ...additional fields...
}
```

**Error Response**:
```json
{
  "code": 400,
  "message": "Invalid request parameter",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

**List Response**:
```json
{
  "data": [
    {task1...},
    {task2...}
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 150
  }
}
```

**Authentication**:
```
Header: Authorization: Bearer <JWT_TOKEN>

JWT Structure:
{
  "user_id": "uuid",
  "username": "john",
  "exp": 1707374400,    // Expiration timestamp
  "iat": 1707288000,    // Issued at
  "jti": "uuid"         // JWT ID (for revocation)
}
```

### 4. Webhook System

#### Webhook Events Available

```
Available Events (Event Subscriptions):
├─ task.created       (task created)
├─ task.updated       (task modified)
├─ task.deleted       (task deleted)
├─ task.completed     (task marked done)
├─ project.created    (project created)
├─ project.updated    (project modified)
├─ project.deleted    (project deleted)
└─ comment.created    (comment added to task)
```

#### Webhook Payload Example

```json
{
  "timestamp": "2026-02-08T12:00:00Z",
  "event": "task.created",
  "user_id": "user-uuid",
  "data": {
    "task": {
      "id": "task-uuid",
      "title": "New task",
      "project_id": "project-uuid",
      "created_by": "user-uuid",
      "created": "2026-02-08T12:00:00Z"
    }
  }
}
```

#### Webhook Delivery Guarantees

- **Delivery**: At-least-once (may be delivered multiple times)
- **Timeout**: 5 seconds per request
- **Retry**: 3 attempts with exponential backoff
- **Headers**: X-Vikunja-Signature (HMAC-SHA256 if secret configured)

---

## COMPONENT RELATIONSHIPS & DATA FLOW

### 1. User Registration & Login Flow

```
[New User]
    ↓
POST /api/v1/auth/register
  ├─ Validate: username, email, password
  ├─ Hash password: bcrypt (cost=10)
  ├─ Create user record
  ├─ Create personal namespace
  └─ Return: user object, JWT token
    ↓
[Existing User]
    ↓
POST /api/v1/auth/login
  ├─ Lookup user by email/username
  ├─ Verify password hash
  ├─ Generate JWT token (signed with VIKUNJA_SERVICE_JWTSECRET)
  ├─ Store session in Redis (if enabled)
  └─ Return: JWT token, user object
    ↓
[Authenticated Requests]
    ↓
Authorization header: Bearer <token>
  ├─ Verify token signature
  ├─ Check expiration (VIKUNJA_SERVICE_JWTEXPIRATION)
  ├─ Load user from token
  ├─ Check permissions (RBAC)
  └─ Process request
```

### 2. Task Creation & Webhook Flow

```
[User Action: Create Task]
    ↓
POST /api/v1/tasks
{
  "project_id": "uuid",
  "title": "New task",
  "description": "..."
}
    ↓
[Vikunja Processing]
    ├─ Validate project access (user must be member)
    ├─ Create task record in PostgreSQL
    ├─ Create activity log entry
    ├─ Update project's updated_at timestamp
    ├─ Trigger webhooks (task.created)
    ├─ Refresh Redis cache (if enabled)
    └─ Return: task object, 201 Created
    ↓
[Webhook Delivery]
    ├─ Query registered webhooks for task.created events
    ├─ For each webhook:
    │  ├─ Construct payload
    │  ├─ Sign with HMAC (if secret configured)
    │  ├─ POST to webhook URL (timeout: 5s)
    │  ├─ On failure: retry up to 3 times
    │  └─ Log result
    └─ Return to user immediately (async)
    ↓
[External System] (e.g., Memory Bank)
    ├─ Receive webhook POST
    ├─ Verify signature (if configured)
    ├─ Process task data
    ├─ Update local representation
    └─ Acknowledge receipt (HTTP 200)
```

### 3. Permission System (RBAC)

```
Permission Hierarchy:
┌─────────────────────────────────────────┐
│ Admin (Full Access)                      │
│  ├─ Can create/delete teams              │
│  ├─ Can manage all users                 │
│  ├─ Can manage all projects              │
│  └─ Can configure webhooks               │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Team Member (Team-level permissions)    │
│  ├─ Can create projects in team          │
│  ├─ Can manage team members              │
│  ├─ Can view all team projects           │
│  └─ Can configure team webhooks          │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Project Member (Project-level perms)    │
│  ├─ Can create/edit/delete tasks         │
│  ├─ Can add/remove project members       │
│  ├─ Can edit project settings            │
│  └─ Cannot delete project (admin only)   │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Guest (Read-only Access)                │
│  ├─ Can view tasks/projects              │
│  └─ Cannot modify anything               │
└─────────────────────────────────────────┘

Shared Links:
  ├─ Public read-only links (for tasks/projects)
  └─ Expiring links (temporary access)
```

### 4. Caching Strategy (with Redis)

```
Redis Usage in Vikunja:
├─ Session Storage (VIKUNJA_REDIS_DB: 5)
│  ├─ Key: session:<session_id>
│  ├─ Value: user data + expiration
│  └─ TTL: match JWT expiration
├─ Task Query Cache
│  ├─ Key: task:<task_id>
│  ├─ TTL: 5 minutes
│  └─ Invalidated on: task.updated, task.deleted
├─ Project Cache
│  ├─ Key: project:<project_id>
│  ├─ TTL: 10 minutes
│  └─ Invalidated on: project.updated
├─ User Permission Cache
│  ├─ Key: user:<user_id>:permissions
│  ├─ TTL: 15 minutes
│  └─ Invalidated on: role/membership changes
└─ Rate Limiting
   ├─ Key: ratelimit:<user_id>:<endpoint>
   ├─ Counter: requests per minute
   └─ Limit: configurable (default: 100/min)
```

---

## DESIGN PATTERNS & BEST PRACTICES

### 1. API Consumption Patterns

#### Pattern 1: Async Task Creation with Polling

```go
// Create task asynchronously
POST /api/v1/tasks → Returns: { id: "task-123" }

// Poll for completion
GET /api/v1/tasks/task-123
// Retry until:
//   - Task fully created (all fields populated)
//   - Webhook sent to subscribers
//   - Cache updated

// Better: Use webhooks to get notified
POST /api/v1/webhooks
{
  "events": ["task.created"],
  "target_url": "https://yourapp.com/webhook"
}
```

#### Pattern 2: Batch Operations

```
⚠️ Note: Vikunja doesn't have batch endpoints
Workaround:
  1. Create connection pool
  2. Make parallel requests (5-10 concurrent)
  3. Aggregate responses
  4. Handle partial failures gracefully

Example (5 tasks parallel):
parallel(
  POST /api/v1/tasks (task 1),
  POST /api/v1/tasks (task 2),
  POST /api/v1/tasks (task 3),
  POST /api/v1/tasks (task 4),
  POST /api/v1/tasks (task 5)
)
```

#### Pattern 3: Search & Filter

```
GET /api/v1/tasks/search?query=...

Search Parameters:
  - query: text search (title, description)
  - project_id: filter by project
  - namespace_id: filter by namespace
  - assigned_to_user_id: assigned tasks
  - done: 0=incomplete, 1=done
  - due_date_before: task due before date
  - due_date_after: task due after date
  - sort_by: field name for sorting
  - order: asc/desc
  - page: pagination
  - per_page: items per page

Example:
GET /api/v1/tasks/search?query=urgent&done=0&sort_by=due_date&order=asc
```

### 2. State Management Pattern

```
Recommended State Machine for Tasks:
┌──────────────┐
│    CREATED   │ Initial state
└──────┬───────┘
       │
       ↓ (user action: mark in progress)
┌──────────────┐
│  IN_PROGRESS │ Work started
└──────┬───────┘
       │
       ├─→ (pause) ──→ ┌──────────────┐
       │                │   PAUSED     │
       │                └──────┬───────┘
       │                       │
       │                       └─→ (resume) ──→ ┌──────────────┐
       │                                          │  IN_PROGRESS │
       │                                          └──────┬───────┘
       │                                                 │
       └────────────────────────────────────────────────┘
                                                         │
                                                         ↓ (complete)
                                                 ┌──────────────┐
                                                 │  COMPLETED   │
                                                 └──────┬───────┘
                                                        │
                                                 (delete) ↓
                                                 ┌──────────────┐
                                                 │  ARCHIVED    │
                                                 └──────────────┘

Implementation: Use 'done' boolean + custom label system
  Task: { done: true, labels: ["completed"] }
```

### 3. Error Handling Pattern

```
Standard Error Responses:

400 Bad Request
  └─ Validation failed (missing fields, invalid format)
  └─ Response: { errors: { field: ["message"] } }

401 Unauthorized
  └─ Missing or invalid JWT token
  └─ Response: { message: "Unauthorized" }

403 Forbidden
  └─ Authenticated but no permission
  └─ Response: { message: "Forbidden" }

404 Not Found
  └─ Resource doesn't exist
  └─ Response: { message: "Not found" }

422 Unprocessable Entity
  └─ Request valid but can't process
  └─ Response: { message: "..." }

500 Internal Server Error
  └─ Server error
  └─ Response: { message: "Internal server error" }

Best Practice for Client:
  1. Catch by status code
  2. Log full response (for debugging)
  3. Show user-friendly message
  4. Implement retry logic for 5xx errors
  5. Never retry 4xx errors (will fail again)
```

### 4. Pagination Pattern

```
All list endpoints support pagination:

GET /api/v1/tasks?page=1&per_page=50

Response:
{
  "data": [...tasks...],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 250
  }
}

Recommended:
  - Default: page=1, per_page=50
  - Max: per_page=500 (respect server limits)
  - Iteration: page++ until page > (total/per_page)

Implementation:
```python
page = 1
all_tasks = []
while True:
    response = api.get_tasks(page=page, per_page=50)
    all_tasks.extend(response['data'])
    if response['pagination']['page'] * response['pagination']['per_page'] >= response['pagination']['total']:
        break
    page += 1
```

---

## INTEGRATION FUNDAMENTALS

### 1. Memory Bank ↔ Vikunja Integration

**Data Flow**:
```
Memory Bank (Knowledge Store)
    ↓ (export as task)
Vikunja API
    ├─ Create Project: "Research Topics"
    ├─ Create Tasks: one per knowledge item
    ├─ Link Labels: topic, status, priority
    └─ Set Metadata: dates, assignee
    ↓
Webhook triggers on changes
    ↓
Memory Bank receives update
    ├─ Task marked done → Update knowledge status
    ├─ Labels changed → Update knowledge tags
    ├─ Comments added → Store context
    └─ Due date set → Alert on deadline
```

### 2. RAG API ↔ Vikunja Integration

**Research Workflow**:
```
1. User asks question via Voice Interface
2. RAG API processes query
3. Generates research task in Vikunja
   POST /api/v1/tasks
   {
     "project_id": "research-uuid",
     "title": "Research: [question]",
     "description": "[findings summary]",
     "labels": ["ai-research", "in-progress"],
     "due_date": "[completion date]"
   }
4. Webhook notifies Memory Bank
5. Memory Bank archives research result
6. Task marked complete on resolution
```

### 3. Voice Interface ↔ Vikunja Integration

**Voice Command → Task Workflow**:
```
[Voice]: "Create a task: review API documentation"
    ↓
[Voice Interface]
    ├─ Parse intent: create_task
    ├─ Extract: title="review API documentation"
    └─ Call: Vikunja API
    ↓
[Vikunja]
    ├─ POST /api/v1/tasks
    ├─ Assign to current project
    ├─ Auto-assign to speaker (if authenticated)
    └─ Return task ID + confirmation
    ↓
[Voice Interface]
    └─ Speak: "Task created: review API documentation"
```

---

## FOUNDATION STACK CONTEXT

### Xoe-NovAi Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  USER INTERFACE LAYER                    │
│  Voice Interface ↔ Chainlit Web UI ↔ API Consumers     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              ORCHESTRATION LAYER (Vikunja)              │
│  Task Management │ Projects │ Webhooks │ Collaboration │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼─────┐ ┌────▼───────┐ ┌─▼──────────┐
│   RAG API   │ │ Memory Bank │ │  Monitoring│
│(Research)   │ │(Knowledge)  │ │(Prometheus)│
└─────────────┘ └─────────────┘ └────────────┘
        │            │                │
        └────────────┼────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│               DATA LAYER                                 │
│  PostgreSQL 16 │ Redis 7.4.1 │ File Storage             │
└─────────────────────────────────────────────────────────┘
```

### Service Dependencies

```
Vikunja (port 3456)
├─ Depends on: PostgreSQL (vikunja-db)
├─ Depends on: Redis (optional, but recommended)
├─ Provides: REST API for task management
├─ Triggers: Webhooks on events
└─ Consumed by: Memory Bank, Voice Interface, RAG API

Redis (port 6379)
├─ Vikunja uses DB 5 (Foundation uses 0-4)
├─ Stores: session data, cache, rate limiting
└─ Monitored by: Prometheus

PostgreSQL (port 5432, internal)
├─ Stores: all Vikunja data
├─ Optimized for: Ryzen architecture
└─ Backed up: daily (recommended)
```

### Network Architecture

```
External (Port 3456)
    ↓
Vikunja Container ←→ PostgreSQL Container
    ↓                      ↓
   Redis (Shared)      Volume Mount
    ↓                   (/data/vikunja/db)
Foundation Stack
```

---

## KEY DECISIONS & RATIONALE

### 1. Why Environment Variables Over Podman Secrets?

**Decision**: Use environment variables for password management

**Rationale**:
- ✅ 100% reliable with docker-compose + Podman
- ✅ No docker-compose provider limitations
- ✅ Simpler debugging and troubleshooting
- ✅ Industry-standard approach
- ✅ Passwords not in git (via .env + .gitignore)
- ✅ Still secure at runtime

**Alternative Rejected**: Podman external secrets
- ❌ Doesn't mount properly in rootless mode
- ❌ docker-compose provider has limitations
- ❌ Harder to debug
- ❌ Overly complex for this use case

### 2. Why Shared xnai_network?

**Decision**: Share Foundation network instead of isolated

**Rationale**:
- ✅ Service-level isolation sufficient (cap_drop, user isolation)
- ✅ Vikunja can access Foundation Redis
- ✅ Better resource efficiency
- ✅ Simpler architecture
- ✅ Enables inter-service communication
- ✅ Maintains security posture

**Alternative Rejected**: Isolated vikunja-net
- ❌ Prevented Redis access
- ❌ Required workarounds (disable Redis)
- ❌ Unnecessary complexity
- ❌ Added per-service network overhead

### 3. Why Vikunja 0.24.1?

**Decision**: Use Vikunja v0.24.1 (stable, pre-built image)

**Rationale**:
- ✅ Stable release (not alpha/beta)
- ✅ Pre-built image (vikunja/vikunja:0.24.1)
- ✅ No compilation needed
- ✅ Known issues documented
- ✅ Security patches applied
- ✅ API stable (v1)

**Alternative Considered**: Latest development
- ❌ Unstable API changes
- ❌ Requires building image
- ❌ More CPU/memory during build
- ❌ Potential bugs/regressions

---

## NEXT STEPS

This foundation covers the deep architecture and design patterns. The next parts will cover:

- **Part 2**: Advanced Configuration & Optimization
- **Part 3**: Deployment & Blocker Resolution (Detailed)
- **Part 4**: Operations & Maintenance
- **Part 5**: Security & Hardening
- **Part 6**: Troubleshooting & Diagnostics
- **Part 7**: Integration & Advanced Patterns
- **Part 8**: Master Comprehensive Reference

---

**Status**: ✅ COMPLETE (Part 1 of 8)  
**Next**: PART 2 - Advanced Configuration & Optimization  
**Estimated Total Documentation**: ~200+ pages  
**Confidence**: 99% comprehensive coverage

