# Metropolis Notification Stream Blueprint

## System Overview
A high-performance, scalable notification system using Redis Streams to handle real-time message delivery across the Metropolis ecosystem.

## Redis Key Structure

### Core Streams
```
notifications:stream:{tenant_id}:{environment}          # Primary notification stream
notifications:dead:letter:{tenant_id}:{environment}     # Failed message handling
notifications:metadata:{tenant_id}                      # System metadata and counters
```

### Consumer Groups
```
notifications:cg:{tenant_id}:{consumer_group}           # Consumer group per service
notifications:cg:webhooks:{tenant_id}                   # Webhook delivery group
notifications:cg:email:{tenant_id}                      # Email delivery group
notifications:cg:sms:{tenant_id}                        # SMS delivery group
```

### Rate Limiting & Tracking
```
notifications:rate:limit:{tenant_id}:{channel_type}     # Rate limiting counters
notifications:delivery:status:{message_id}              # Delivery status tracking
notifications:user:prefs:{user_id}                      # User notification preferences
```

## Message Schema

```json
{
  "id": "msg_<timestamp>_<uuid>",                      // Unique message ID
  "timestamp": 1672531200000,                          // Unix timestamp in milliseconds
  "tenant_id": "tenant_abc123",                        // Tenant identifier
  "channel": "email|sms|push|webhook|in_app",          // Delivery channel
  "priority": "high|medium|low",                       // Message priority
  
  // Recipient Information
  "recipient": {
    "user_id": "user_xyz789",
    "email": "user@example.com",
    "phone": "+1234567890",
    "device_tokens": ["token1", "token2"]
  },
  
  // Message Content
  "content": {
    "subject": "Notification Subject",
    "body": "Main message content",
    "template_id": "welcome_email",                    // Optional template reference
    "variables": {                                     // Template variables
      "name": "John Doe",
      "action_url": "https://app.example.com/verify"
    }
  },
  
  // Delivery Configuration
  "delivery_config": {
    "retry_attempts": 3,
    "retry_backoff_ms": 5000,
    "timeout_ms": 30000,
    "expires_at": 1672617600000                       // Message expiration timestamp
  },
  
  // Metadata
  "metadata": {
    "source_service": "auth-service",
    "event_type": "user_registered",
    "correlation_id": "corr_987654",
    "tags": ["welcome", "onboarding"]
  }
}
```

## Stream Configuration

### Stream Settings
```bash
# Max length per stream (prevent memory exhaustion)
XTRIM notifications:stream:tenant_abc123:prod MAXLEN ~ 1000000

# Consumer group creation
XGROUP CREATE notifications:stream:tenant_abc123:prod notifications:cg:email:tenant_abc123 $ MKSTREAM
```

### Consumer Group Settings
```bash
# Acknowledge timeout (30 seconds)
XGROUP SETID notifications:stream:tenant_abc123:prod notifications:cg:email:tenant_abc123 0
```

## High-Level Architecture

```
[Producers] → [Redis Stream] → [Consumer Groups] → [Delivery Services] → [End Users]
    │              │                 │                   │
    │              │                 ├── Email Service   → SMTP/Email Providers
    │              │                 ├── SMS Service     → SMS Gateways
    │              │                 ├── Push Service    → APNS/FCM
    │              │                 └── Webhook Service → HTTP Endpoints
    │              │
    │              └── [Dead Letter Queue] → [Error Handling & Retry]
    │
    └── [Monitoring & Metrics] → [Prometheus/Grafana]
```

## Example Usage Patterns

### Sending a Notification
```bash
XADD notifications:stream:tenant_abc123:prod * \
    id "msg_1672531200000_a1b2c3d4" \
    tenant_id "tenant_abc123" \
    channel "email" \
    priority "high" \
    recipient '{"user_id": "user_xyz789", "email": "user@example.com"}' \
    content '{"subject": "Welcome!", "body": "Welcome to Metropolis!"}' \
    metadata '{"source_service": "auth-service", "event_type": "user_registered"}'
```

### Consuming Messages
```bash
XREADGROUP GROUP notifications:cg:email:tenant_abc123 email_worker_1 \
    COUNT 10 BLOCK 5000 STREAMS notifications:stream:tenant_abc123:prod >
```

## Monitoring & Metrics Key Metrics
- **Throughput**: Messages processed per second
- **Latency**: End-to-end delivery time
- **Error Rate**: Failed deliveries percentage
- **Backlog**: Pending messages in streams
- **Consumer Lag**: Delay in message processing

This blueprint provides a scalable foundation for real-time notification delivery with built-in reliability, monitoring, and extensibility features.
