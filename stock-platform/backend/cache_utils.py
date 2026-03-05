"""
외부 API 호출 결과 TTL 캐시 (예: 10분).
캐시 키 예: ("price", "AAPL"), ("rec", "AAPL") 등.
"""
import threading
import time
from typing import Any, Optional, Tuple

# (key_tuple -> (value, expires_at))
_cache: dict = {}
_lock = threading.Lock()
_DEFAULT_TTL = 600  # 10분


def cache_get(key: Tuple[str, ...], ttl: int = _DEFAULT_TTL) -> Optional[Any]:
    """캐시에서 조회. 만료되었거나 없으면 None."""
    with _lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        val, expires_at = entry
        if time.time() > expires_at:
            del _cache[key]
            return None
        return val


def cache_set(key: Tuple[str, ...], value: Any, ttl: int = _DEFAULT_TTL) -> None:
    """캐시에 저장."""
    with _lock:
        _cache[key] = (value, time.time() + ttl)


def cache_get_or_set(
    key: Tuple[str, ...],
    fetch_fn,
    *args,
    ttl: int = _DEFAULT_TTL,
    **kwargs,
) -> Any:
    """캐시에 있으면 반환, 없으면 fetch_fn(*args, **kwargs) 호출 후 저장·반환."""
    val = cache_get(key, ttl)
    if val is not None:
        return val
    try:
        val = fetch_fn(*args, **kwargs)
        if val is not None:
            cache_set(key, val, ttl)
        return val
    except Exception:
        return None
