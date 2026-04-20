from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid
import logging
from datetime import datetime

from app.api.deps import get_current_admin, get_current_user
from app.models.database import get_db
from app.models.domain import ChatSession, ChatMessage, User
from app.services.rag_service import retrieve_from_milvus
from app.services.llm_service import generate_rag_answer

logger = logging.getLogger(__name__)

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
async def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session_id = request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        # Create new session
        new_session = ChatSession(id=session_id, user_id=current_user.id, title=request.query[:20])
        db.add(new_session)
        db.commit()

    # Save user message
    user_msg = ChatMessage(session_id=session_id, role="user", content=request.query)
    db.add(user_msg)
    
    try:
        # 1. Retrieve relevant contexts from Milvus
        retrieved_docs = retrieve_from_milvus(request.query, top_k=3)
        
        sources = []
        context_parts = []
        for doc in retrieved_docs:
            source_info = f"{doc['collection']} (score: {doc['score']:.2f}): {doc['source']}"
            sources.append(source_info)
            context_parts.append(f"[来源: {doc['source']}]\n{doc['text']}")
            
        context_str = "\n\n".join(context_parts)
        
        if not context_str:
            context_str = "没有找到相关的知识库背景信息。"
            
        # 2. Generate answer using Qwen LLM
        answer = generate_rag_answer(context=context_str, query=request.query)
        
    except Exception as e:
        logger.error(f"Error generating RAG answer: {e}")
        answer = "抱歉，系统处理您的请求时遇到了错误，请稍后再试。"
        sources = []
    
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
async def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()
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
async def get_all_history(user_id: str | None = None, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    # For admin dashboard
    q = db.query(ChatSession)
    if user_id:
        q = q.filter(ChatSession.user_id == user_id)
    sessions = q.order_by(ChatSession.created_at.desc()).all()
    user_ids = list({s.user_id for s in sessions})
    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    user_map = {u.id: u.username for u in users}
    res = []
    for s in sessions:
        msgs = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).order_by(ChatMessage.created_at.asc()).all()
        res.append({
            "session_id": s.id,
            "user_id": s.user_id,
            "username": user_map.get(s.user_id, ""),
            "title": s.title,
            "created_at": s.created_at,
            "messages": [{"role": m.role, "content": m.content, "time": m.created_at} for m in msgs]
        })
    return res
