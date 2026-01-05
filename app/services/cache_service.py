# app/services/cache_service.py
from app.core.redis import redis_client
from app.core.config import settings
from typing import Optional, List, Dict
import json
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Redis caching service [web:4]"""
    
    @staticmethod
    async def cache_generated_questions(
        content_id: int,
        difficulty: str,
        questions: List[Dict]
    ) -> None:
        """Cache generated questions [web:4]"""
        cache_key = f"questions:content:{content_id}:difficulty:{difficulty}"
        
        try:
            await redis_client.set(
                cache_key,
                {"questions": questions},
                ttl=settings.CACHE_TTL_QUESTIONS
            )
            logger.info(f"Cached {len(questions)} questions for content {content_id}")
        except Exception as e:
            logger.error(f"Failed to cache questions: {e}")
    
    @staticmethod
    async def get_cached_questions(
        content_id: int,
        difficulty: str
    ) -> Optional[List[Dict]]:
        """Get cached questions [web:4]"""
        cache_key = f"questions:content:{content_id}:difficulty:{difficulty}"
        
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.info(f"Cache hit for content {content_id}")
                return cached.get("questions", [])
        except Exception as e:
            logger.error(f"Failed to get cached questions: {e}")
        
        return None
    
    @staticmethod
    async def cache_user_analytics(user_id: int, analytics_data: Dict) -> None:
        """Cache user analytics [web:4]"""
        cache_key = f"analytics:user:{user_id}"
        
        try:
            await redis_client.set(
                cache_key,
                analytics_data,
                ttl=settings.CACHE_TTL_ANALYTICS
            )
        except Exception as e:
            logger.error(f"Failed to cache analytics: {e}")
    
    @staticmethod
    async def get_cached_analytics(user_id: int) -> Optional[Dict]:
        """Get cached analytics [web:4]"""
        cache_key = f"analytics:user:{user_id}"
        
        try:
            return await redis_client.get(cache_key)
        except Exception as e:
            logger.error(f"Failed to get cached analytics: {e}")
            return None
    
    @staticmethod
    async def invalidate_user_cache(user_id: int) -> None:
        """Invalidate user-related caches"""
        try:
            await redis_client.delete(f"analytics:user:{user_id}")
            logger.info(f"Invalidated cache for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
