from redis.asyncio import Redis
from src.utils.config import Settings

settings = Settings()

async def get_redis():
    redis = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()