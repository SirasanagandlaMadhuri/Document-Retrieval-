from app import cache

def get_cached_result(cache_key: str):
    """Retrieves a cached result by key."""
    return cache.get(cache_key)

def set_cached_result(cache_key: str, data, timeout=300):
    """Sets a cached result with a timeout."""
    cache.set(cache_key, data, timeout=timeout)
    return True

def check_rate_limiting(user_id: str, db):
    """Enforce rate-limiting on API requests."""
    request_count = db.get_user_request_count(user_id)
    if request_count and request_count >= 5:
        raise ValueError("Too many requests. Rate limit exceeded.")
    return True
 
