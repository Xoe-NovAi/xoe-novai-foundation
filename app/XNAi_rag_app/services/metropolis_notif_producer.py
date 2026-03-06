```python
"""
Producer for Metropolis Notification Stream using Redis Streams (XADD)
Schema validation and async implementation using AnyIO and redis-py (asyncio)
"""

import anyio
from redis.asyncio import Redis
from typing import Dict, Any, Optional
import json
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationSchema(BaseModel):
    """Pydantic schema for notification validation"""
    event_id: str = Field(..., min_length=1, max_length=255)
    event_type: str = Field(..., min_length=1, max_length=100)
    source: str = Field(..., min_length=1, max_length=100)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=5)
    ttl_seconds: Optional[int] = Field(default=None, ge=1)


class NotificationProducer:
    """Async producer for Metropolis Notification Stream"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", stream_key: str = "metropolis:notifications"):
        self.redis_url = redis_url
        self.stream_key = stream_key
        self.redis: Optional[Redis] = None
    
    async def connect(self) -> None:
        """Establish Redis connection"""
        try:
            self.redis = Redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            await self.redis.ping()
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")
    
    async def validate_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate notification against schema and prepare for Redis"""
        try:
            # Validate and convert using Pydantic
            validated = NotificationSchema(**notification_data)
            
            # Convert to dict with serializable values
            redis_data = validated.dict()
            redis_data['timestamp'] = redis_data['timestamp'].isoformat()
            
            return redis_data
            
        except ValidationError as e:
            logger.error(f"Notification validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            raise
    
    async def send_notification(self, notification_data: Dict[str, Any]) -> str:
        """
        Send validated notification to Redis Stream using XADD
        
        Args:
            notification_data: Dictionary containing notification data
            
        Returns:
            Message ID of the added stream entry
        """
        if not self.redis:
            raise ConnectionError("Redis client not connected")
        
        try:
            # Validate and prepare notification
            validated_data = await self.validate_notification(notification_data)
            
            # Convert to Redis stream format (flat key-value pairs)
            stream_data = {}
            for key, value in validated_data.items():
                if isinstance(value, (dict, list)):
                    # Serialize complex objects to JSON
                    stream_data[key] = json.dumps(value)
                else:
                    stream_data[key] = str(value)
            
            # Add to Redis stream with automatic ID generation (*)
            message_id = await self.redis.xadd(
                name=self.stream_key,
                fields=stream_data,
                maxlen=10000,  # Optional: cap stream length
                approximate=True  # Optional: allow approximate trimming for performance
            )
            
            logger.info(f"Notification sent successfully: {message_id}")
            return message_id
            
        except ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            raise
    
    async def send_batch_notifications(self, notifications: list[Dict[str, Any]]) -> list[str]:
        """Send multiple notifications in a batch"""
        message_ids = []
        for notification in notifications:
            try:
                message_id = await self.send_notification(notification)
                message_ids.append(message_id)
            except Exception as e:
                logger.error(f"Failed to send batch notification: {e}")
                # Continue with remaining notifications
                continue
        
        return message_ids


async def main():
    """Example usage of the NotificationProducer"""
    producer = NotificationProducer()
    
    try:
        await producer.connect()
        
        # Example notification
        notification = {
            "event_id": "user_login_12345",
            "event_type": "user.authentication",
            "source": "auth-service",
            "payload": {
                "user_id": "user_123",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0"
            },
            "priority": 2,
            "ttl_seconds": 3600
        }
        
        # Send notification
        message_id = await producer.send_notification(notification)
        print(f"Notification sent with ID: {message_id}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        await producer.disconnect()


if __name__ == "__main__":
    anyio.run(main)
```

This implementation provides:

1. **Schema Validation**: Uses Pydantic for robust schema validation with proper field constraints
2. **Redis Stream Integration**: Implements XADD with automatic ID generation and optional stream trimming
3. **Async Architecture**: Fully async using AnyIO and redis-py's asyncio support
4. **Error Handling**: Comprehensive error handling and logging
5. **Serialization**: Proper handling of complex data types through JSON serialization
6. **Batch Operations**: Support for sending multiple notifications
7. **Connection Management**: Proper connection lifecycle management

Key features:
- Pydantic schema validation ensures data integrity
- Automatic timestamp generation
- Configurable stream length limits
- Proper error handling and logging
- Async/await pattern throughout
- No Torch dependencies (as requested)

The producer validates notifications against the schema, converts them to Redis-friendly format, and sends them to the specified stream using XADD with automatic message ID generation.
