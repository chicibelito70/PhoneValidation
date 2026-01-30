from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import APIKeyCreate, APIKeyResponse
from ..services import create_api_key
from ..utils.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=dict)
def create_key(key_data: APIKeyCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    api_key, db_key = create_api_key(db, current_user.id, key_data)
    return {"api_key": api_key, "id": db_key.id}

@router.get("/", response_model=list[APIKeyResponse])
def list_keys(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    keys = db.query(APIKey).filter(APIKey.owner_id == current_user.id).all()
    return keys