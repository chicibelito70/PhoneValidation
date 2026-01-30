import secrets
import hashlib
from sqlalchemy.orm import Session
from ..models import APIKey
from ..schemas import APIKeyCreate

def generate_api_key():
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str):
    return hashlib.sha256(api_key.encode()).hexdigest()

def create_api_key(db: Session, user_id: int, key_data: APIKeyCreate):
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    key_prefix = api_key[:10]
    db_key = APIKey(
        key_hash=key_hash,
        key_prefix=key_prefix,
        owner_id=user_id,
        plan=key_data.plan
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return api_key, db_key

def get_api_key_by_hash(db: Session, key_hash: str):
    return db.query(APIKey).filter(APIKey.key_hash == key_hash).first()

def update_usage(db: Session, api_key_id: int):
    db_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
    if db_key:
        db_key.daily_usage += 1
        db_key.monthly_usage += 1
        db.commit()

def reset_usage(db: Session):
    # Reset monthly usage on 1st of month, etc.
    pass