import redis
import os
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import get_api_key_by_hash, hash_api_key
from ..models import Subscription

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

async def api_key_middleware(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key required")

    key_hash = hash_api_key(api_key)
    db: Session = next(get_db())
    db_key = get_api_key_by_hash(db, key_hash)
    if not db_key or db_key.status != 'active':
        raise HTTPException(status_code=403, detail="Invalid or inactive API Key")

    # Check subscription status
    user = db_key.owner
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.status == 'active').first()
    if not subscription:
        raise HTTPException(status_code=403, detail="No active subscription")

    # Check rate limit
    if not check_rate_limit(db_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Update usage
    from ..services import update_usage
    update_usage(db, db_key.id)

    response = await call_next(request)
    return response

def check_rate_limit(api_key):
    plan = api_key.plan
    if not plan:
        return False
    limit = plan.daily_limit if plan.daily_limit else 100  # Default
    if limit == 0:  # Unlimited
        return True

    key = f"rate_limit:{api_key.id}"
    current = redis_client.get(key)
    if current and int(current) >= limit:
        return False
    redis_client.incr(key)
    redis_client.expire(key, 86400)  # 1 day
    return True