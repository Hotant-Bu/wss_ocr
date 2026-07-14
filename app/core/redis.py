import redis.asyncio as aioredis
from typing import Optional
from app.config import settings


class RedisManager:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        if self.redis is None:
            self.redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=settings.REDIS_DECODE_RESPONSES,
                encoding="utf-8"
            )
    
    async def close(self):
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[str]:
        if not self.redis:
            await self.connect()
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, expire: int = None):
        if not self.redis:
            await self.connect()
        await self.redis.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        if not self.redis:
            await self.connect()
        await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        if not self.redis:
            await self.connect()
        return await self.redis.exists(key) > 0
    
    async def expire(self, key: str, seconds: int):
        if not self.redis:
            await self.connect()
        await self.redis.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        if not self.redis:
            await self.connect()
        return await self.redis.ttl(key)


redis_manager = RedisManager()


async def get_redis():
    if not redis_manager.redis:
        await redis_manager.connect()
    return redis_manager.redis
