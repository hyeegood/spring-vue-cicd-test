import os
import time
from typing import Any, Optional

REDIS_URL = os.getenv("REDIS_URL", "").strip()
_redis_client = None
_memory_cache = {}
_memory_ts = {}
_memory_ttl = {}  # 키별 TTL (초)
DEFAULT_TTL = 60

def _get_redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    if not REDIS_URL:
        return None
    try:
        import redis
        _redis_client = redis.from_url(REDIS_URL)
        _redis_client.ping()
        return _redis_client
    except Exception:
        return None

def cache_get(key: str) -> Optional[Any]:
    r = _get_redis()
    if r:
        try:
            import json
            raw = r.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None
    if key not in _memory_cache:
        return None
    ttl = _memory_ttl.get(key, DEFAULT_TTL)
    if time.time() - _memory_ts.get(key, 0) > ttl:
        _memory_cache.pop(key, None)
        _memory_ts.pop(key, None)
        _memory_ttl.pop(key, None)
        return None
    return _memory_cache[key]

def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    r = _get_redis()
    if r:
        try:
            import json
            r.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            pass
        return
    _memory_cache[key] = value
    _memory_ts[key] = time.time()
    _memory_ttl[key] = ttl

def cache_invalidate(key: str) -> None:
    _memory_cache.pop(key, None)
    _memory_ts.pop(key, None)
    _memory_ttl.pop(key, None)
    r = _get_redis()
    if r:
        try:
            r.delete(key)
        except Exception:
            pass
