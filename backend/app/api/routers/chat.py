from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid
import logging
import json
from datetime import datetime

from app.api.deps import get_current_admin, get_current_user
from app.models.database import get_db, SessionLocal
from app.models.domain import ChatSession, ChatMessage, User
from app.services.rag_service import retrieve_from_milvus
from app.services.llm_service import generate_rag_answer_stream

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    domain: Optional[str] = "bidding"

@router.post("")
@router.post("/", include_in_schema=False)
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
    db.commit()

    async def generate_response_stream():
        full_answer = ""
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
            
            # Send initial metadata (session_id and sources)
            init_data = {"session_id": session_id, "sources": sources, "type": "meta"}
            yield f"data: {json.dumps(init_data, ensure_ascii=False)}\n\n"
            
            # 2. Generate answer using Qwen LLM stream
            async for chunk in generate_rag_answer_stream(context=context_str, query=request.query):
                if chunk:
                    full_answer += chunk
                    chunk_data = {"chunk": chunk, "type": "chunk"}
                    yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                    
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            logger.error(f"Error generating RAG answer: {e}")
            err_data = {"error": "抱歉，系统处理您的请求时遇到了错误，请稍后再试。", "type": "error"}
            yield f"data: {json.dumps(err_data, ensure_ascii=False)}\n\n"
        finally:
            # Save assistant message using a new DB session since we are inside a generator
            db_gen = SessionLocal()
            try:
                assistant_msg = ChatMessage(session_id=session_id, role="assistant", content=full_answer)
                db_gen.add(assistant_msg)
                db_gen.commit()
            except Exception as db_e:
                logger.error(f"Failed to save assistant message: {db_e}")
            finally:
                db_gen.close()

    return StreamingResponse(generate_response_stream(), media_type="text/event-stream")

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
