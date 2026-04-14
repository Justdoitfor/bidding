from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.models.database import get_db
from app.models.domain import User

router = APIRouter()


class UserItem(BaseModel):
    id: str
    username: str
    is_admin: bool
    is_active: bool


class UpdateUserRequest(BaseModel):
    is_admin: bool | None = None
    is_active: bool | None = None


@router.get("/", response_model=list[UserItem])
def list_users(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserItem(id=u.id, username=u.username, is_admin=u.is_admin, is_active=u.is_active) for u in users]


@router.patch("/{user_id}", response_model=UserItem)
def update_user(user_id: str, req: UpdateUserRequest, _: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if req.is_admin is not None:
        user.is_admin = req.is_admin
    if req.is_active is not None:
        user.is_active = req.is_active

    db.commit()
    db.refresh(user)
    return UserItem(id=user.id, username=user.username, is_admin=user.is_admin, is_active=user.is_active)


@router.delete("/{user_id}")
def delete_user(user_id: str, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 级联删除相关的聊天记录 (简单处理)
    from app.models.domain import ChatSession, ChatMessage
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
    for session in sessions:
        db.query(ChatMessage).filter(ChatMessage.session_id == session.id).delete()
    db.query(ChatSession).filter(ChatSession.user_id == user_id).delete()
    
    db.delete(user)
    db.commit()
    return {"message": "用户已删除"}

