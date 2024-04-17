from quart import abort, request
from limits.aio.strategies import MovingWindowRateLimiter
from limits.storage import RedisStorage
from limits import RateLimitItemPerMinute
from aredis import StrictRedis

async def init_limiter(redis_url):
    redis_client = StrictRedis.from_url(redis_url, decode_responses=True)
    storage = RedisStorage(redis_client)
    return MovingWindowRateLimiter(storage)

class DummyLimiter:
    def limit(self, *args, **kwargs):
        def decorator(f):
            return f
        return decorator

async def rate_limit_middleware(app, limiter):
    @app.middleware("before_request")
    async def rate_limit():
        if isinstance(limiter, DummyLimiter):
            return  # Skip rate limiting if using the dummy limiter
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        limit = RateLimitItemPerMinute(5)  # Set the rate limit
        if not await limiter.hit(limit, client_ip):
            abort(429, description="Rate limit exceeded")
