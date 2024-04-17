
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def init_limiter(app):
    from redis import Redis
    redis_uri = app.config.get('REDIS_URI', 'redis://localhost:6379/0')
    redis = Redis.from_url(redis_uri, decode_responses=True, ssl=app.config.get('REDIS_SSL', False))
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=redis_uri,
        default_limits=["50 per hour", "5 per minute"]
    )
    
    return limiter
