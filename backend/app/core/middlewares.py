import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
import redis.asyncio as redis

logger = logging.getLogger("api_requests")

# Redis connection for rate limiting
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {process_time:.2f}ms | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)
            
        # 排除无需限流的路径
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        # 简单滑动窗口限流：每分钟 120 次请求
        limit = 120
        window = 60
        key = f"rate_limit:{client_ip}"
        
        try:
            current_time = int(time.time())
            pipeline = redis_client.pipeline()
            pipeline.zremrangebyscore(key, 0, current_time - window)
            pipeline.zadd(key, {str(current_time): current_time})
            pipeline.zcard(key)
            pipeline.expire(key, window)
            results = await pipeline.execute()
            
            request_count = results[2]
            
            if request_count > limit:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={"code": 429, "message": "请求过于频繁，请稍后再试", "data": None}
                )
        except Exception as e:
            logger.warning(f"Rate limiter failed, bypassing: {e}")
            
        return await call_next(request)
