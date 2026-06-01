import time
from fastapi import Request
from app.db.mongodb import get_mongo_db
from app.core.config import settings


async def log_request_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000

    try:
        db = get_mongo_db()
        await db[settings.MONGO_API_LOGS_COLLECTION].insert_one({
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration, 2),
            "client_ip": request.client.host if request.client else "unknown",
            "timestamp": int(time.time()),
        })
    except Exception:
        pass

    return response
