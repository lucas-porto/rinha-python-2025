import os
from functools import lru_cache


class Settings:
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    pp_default: str = os.getenv("PROCESSOR_DEFAULT_URL")
    pp_fallback: str = os.getenv("PROCESSOR_FALLBACK_URL")
    health_cache_ttl: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
