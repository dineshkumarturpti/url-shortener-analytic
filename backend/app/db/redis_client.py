import redis

from app.core.config import settings

redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def cache_key_for_code(short_code: str) -> str:
    return f"shorturl:{short_code}"


def get_cached_url(short_code: str) -> str | None:
    return redis_client.get(cache_key_for_code(short_code))


def set_cached_url(short_code: str, long_url: str) -> None:
    redis_client.setex(cache_key_for_code(short_code), settings.cache_ttl_seconds, long_url)


def invalidate_cached_url(short_code: str) -> None:
    redis_client.delete(cache_key_for_code(short_code))
