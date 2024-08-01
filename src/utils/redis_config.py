import aioredis
from src.utils.config import Settings

settings = Settings()

async def get_redis():
    redis = await aioredis.create_redis_pool(settings.REDIS_URL)
    try:
        yield redis
    finally:
        redis.close()
        await redis.wait_closed()