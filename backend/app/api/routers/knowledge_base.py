from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from app.models.database import get_db
from app.models.domain import KnowledgeBase, User
from app.api.deps import get_current_user

router = APIRouter()

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("", response_model=List[KnowledgeBaseResponse])
def get_knowledge_bases(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Isolate by tenant
    kbs = db.query(KnowledgeBase).filter(KnowledgeBase.tenant_id == current_user.tenant_id).all()
    return kbs

@router.post("", response_model=KnowledgeBaseResponse)
def create_knowledge_base(
    kb: KnowledgeBaseCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    new_kb = KnowledgeBase(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        name=kb.name,
        description=kb.description
    )
    db.add(new_kb)
    db.commit()
    db.refresh(new_kb)
    return new_kb
