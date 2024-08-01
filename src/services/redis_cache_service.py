from redis.asyncio import Redis
from src.utils.redis_config import get_redis
from src.utils.error_handling import AppException

class RedisCacheService:
    def __init__(self):
        self.redis: Redis = None

    async def initialize(self):
        self.redis = await anext(get_redis())

    async def set(self, key: str, value: str, expire: int = None):
        if not self.redis:
            raise AppException(status_code=500, detail="Redis connection not initialized")
        try:
            await self.redis.set(key, value, ex=expire)
        except Exception as e:
            raise AppException(status_code=500, detail=f"Failed to set cache: {str(e)}")

    async def get(self, key: str):
        if not self.redis:
            raise AppException(status_code=500, detail="Redis connection not initialized")
        try:
            return await self.redis.get(key)
        except Exception as e:
            raise AppException(status_code=500, detail=f"Failed to get cache: {str(e)}")

    async def geoadd(self, key: str, longitude: float, latitude: float, member: str):
        if not self.redis:
            raise AppException(status_code=500, detail="Redis connection not initialized")
        try:
            await self.redis.geoadd(key, (longitude, latitude, member))
        except Exception as e:
            raise AppException(status_code=500, detail=f"Failed to add geospatial data: {str(e)}")

    async def georadius(self, key: str, longitude: float, latitude: float, radius: float, unit: str = 'km'):
        if not self.redis:
            raise AppException(status_code=500, detail="Redis connection not initialized")
        try:
            return await self.redis.georadius(key, longitude, latitude, radius, unit=unit)
        except Exception as e:
            raise AppException(status_code=500, detail=f"Failed to query geospatial data: {str(e)}")

    async def close(self):
        if self.redis:
            await self.redis.close()