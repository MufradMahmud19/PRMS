from functools import wraps
from flask import current_app
from .app_extensions import cache

def cache_response(timeout=None):
    """
    Decorator to cache route responses.
    Usage:
        @bp.route('/some-route')
        @cache_response(timeout=300)  # Cache for 5 minutes
        def some_route():
            return jsonify({'data': 'some data'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get cached response
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            
            # If not cached, execute function and cache result
            response = f(*args, **kwargs)
            cache.set(cache_key, response, timeout=timeout or current_app.config['CACHE_DEFAULT_TIMEOUT'])
            return response
        return decorated_function
    return decorator

def invalidate_cache(*cache_keys):
    """
    Function to invalidate specific cache keys.
    Usage:
        invalidate_cache('some_route:arg1:arg2')
    """
    for key in cache_keys:
        cache.delete(key)

def clear_all_cache():
    """Clear all cached data."""
    cache.clear() 