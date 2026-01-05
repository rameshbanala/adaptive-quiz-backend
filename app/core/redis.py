# app/core/redis.py
import redis.asyncio as redis
from app.core.config import settings
from typing import Optional
import json


class RedisClient:
    """Redis cache client for question caching [web:4]"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        self.redis = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[dict]:
        """Get cached value"""
        if not self.redis:
            return None
        
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: dict, ttl: int = 3600):
        """Set cached value with TTL"""
        if self.redis:
            await self.redis.setex(
                key,
                ttl,
                json.dumps(value)
            )
    
    async def delete(self, key: str):
        """Delete cached value"""
        if self.redis:
            await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if self.redis:
            return await self.redis.exists(key) > 0
        return False


# Create Redis client instance
redis_client = RedisClient()
