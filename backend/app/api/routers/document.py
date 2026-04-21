from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import shutil
import uuid
import logging
from datetime import datetime
from typing import List

from app.models.database import get_db
from app.models.domain import Document, KnowledgeBase, User
from app.api.deps import get_current_user

# Import the existing ingestion pipeline
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scripts.import_real_data import process_mysql_file, process_milvus_file

logger = logging.getLogger(__name__)

router = APIRouter()

class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str
    document_id: str

class DocumentResponse(BaseModel):
    id: str
    kb_id: str
    filename: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

def async_process_file(file_path: str, original_filename: str, document_id: str, db_session: Session):
    logger.info(f"Background task started for {file_path} with original name {original_filename}")
    doc = db_session.query(Document).filter(Document.id == document_id).first()
    if doc:
        doc.status = "processing"
        db_session.commit()
        
    try:
        # Process structural data to MySQL (Upsert) - Auto detects table type using original filename
        # We need to temporarily rename or pass the original filename to the processor
        # Since import_real_data relies on the filename string, let's create a symlink or rename it
        import_path = os.path.join(os.path.dirname(file_path), f"{document_id}_{original_filename}")
        os.rename(file_path, import_path)
        
        process_mysql_file(import_path, db_session=db_session)
        process_milvus_file(import_path)
        
        logger.info(f"Background task completed successfully for {import_path}")
        
        if doc:
            doc.status = "success"
            db_session.commit()
    except Exception as e:
        logger.error(f"Background task failed for {file_path}: {e}")
        if doc:
            doc.status = "failed"
            db_session.commit()
    finally:
        db_session.close()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    kb_id: str = Form(None), # Made optional for backward compatibility
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx') or file.filename.endswith('.json')):
        raise HTTPException(status_code=400, detail="Only CSV, XLSX, and JSON files are supported.")

    # Validate KB access if provided
    if kb_id:
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.tenant_id == current_user.tenant_id).first()
        if not kb:
            raise HTTPException(status_code=403, detail="无权访问该知识库或知识库不存在")

    # Create temp directory
    temp_dir = "/tmp/bidding_uploads"
    os.makedirs(temp_dir, exist_ok=True)

    # Save uploaded file
    file_extension = os.path.splitext(file.filename)[1]
    doc_id = str(uuid.uuid4())
    temp_file_path = os.path.join(temp_dir, f"{doc_id}{file_extension}")

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create document record
    new_doc = Document(
        id=doc_id,
        kb_id=kb_id if kb_id else "global",
        filename=file.filename,
        status="uploaded",
        file_path=temp_file_path
    )
    db.add(new_doc)
    db.commit()

    # Add processing to background task
    from app.models.database import SessionLocal
    bg_db = SessionLocal()
    background_tasks.add_task(async_process_file, temp_file_path, file.filename, doc_id, bg_db)

    return UploadResponse(
        filename=file.filename,
        status="processing",
        message="File uploaded successfully. System will automatically detect the data type and ingest it into MySQL and Milvus.",
        document_id=doc_id
    )

@router.get("", response_model=List[DocumentResponse])
def get_documents(
    kb_id: str = None, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    query = db.query(Document)
    if kb_id:
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.tenant_id == current_user.tenant_id).first()
        if not kb:
            raise HTTPException(status_code=403, detail="无权访问该知识库")
        query = query.filter(Document.kb_id == kb_id)
    
    return query.all()
