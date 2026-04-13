from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.models.database import get_db
from app.models.domain import ChatSession, ChatMessage, Company, Zhaobiao

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    domain: Optional[str] = "bidding"

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: list

@router.post("/", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    session_id = request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        # Create new session
        new_session = ChatSession(id=session_id, user_id="demo_user", title=request.query[:20])
        db.add(new_session)
        db.commit()

    # Save user message
    user_msg = ChatMessage(session_id=session_id, role="user", content=request.query)
    db.add(user_msg)
    
    # Mock RAG retrieval logic based on local SQLite
    # For a real system, it would search Milvus first, then MySQL.
    answer = f"这是一个关于“{request.query}”的智能回答。数据来源：模拟问答库。"
    sources = []
    
    # Simple mock: if query contains company, search company table
    if "公司" in request.query or "企业" in request.query:
        comps = db.query(Company).limit(1).all()
        if comps:
            answer = f"查找到相关企业：{comps[0].company_name}，法人：{comps[0].legal_rep}，状态：{comps[0].status}。"
            sources.append("企业库")
    
    # Save assistant message
    assistant_msg = ChatMessage(session_id=session_id, role="assistant", content=answer)
    db.add(assistant_msg)
    db.commit()
    
    return ChatResponse(
        answer=answer,
        session_id=session_id,
        sources=sources
    )

@router.get("/history")
async def get_history(user_id: str = "demo_user", db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc()).all()
    res = []
    for s in sessions:
        msgs = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).order_by(ChatMessage.created_at.asc()).all()
        res.append({
            "session_id": s.id,
            "title": s.title,
            "created_at": s.created_at,
            "messages": [{"role": m.role, "content": m.content, "time": m.created_at} for m in msgs]
        })
    return res

@router.get("/admin/history")
async def get_all_history(db: Session = Depends(get_db)):
    # For admin dashboard
    sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()
    res = []
    for s in sessions:
        msgs = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).order_by(ChatMessage.created_at.asc()).all()
        res.append({
            "session_id": s.id,
            "user_id": s.user_id,
            "title": s.title,
            "created_at": s.created_at,
            "messages": [{"role": m.role, "content": m.content, "time": m.created_at} for m in msgs]
        })
    return res
