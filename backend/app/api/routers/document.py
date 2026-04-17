from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import shutil
import uuid
import logging

from app.models.database import get_db
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

def async_process_file(file_path: str, table_type: str):
    logger.info(f"Background task started for {file_path} (table: {table_type})")
    try:
        # Process structural data to MySQL (Upsert)
        process_mysql_file(file_path, table_type)
        # Process unstructured data to Milvus (Semantic Chunking & Embedding)
        process_milvus_file(file_path, table_type)
        logger.info(f"Background task completed successfully for {file_path}")
    except Exception as e:
        logger.error(f"Background task failed for {file_path}: {e}")
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    table_type: str = Form(...)
):
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx') or file.filename.endswith('.json')):
        raise HTTPException(status_code=400, detail="Only CSV, XLSX, and JSON files are supported.")
        
    supported_types = ["company", "law", "product", "zhaobiao", "zhongbiao"]
    if table_type not in supported_types:
        raise HTTPException(status_code=400, detail=f"Unknown table type: {table_type}. Supported: {supported_types}")

    # Create temp directory
    temp_dir = "/tmp/bidding_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save uploaded file
    file_extension = os.path.splitext(file.filename)[1]
    temp_file_path = os.path.join(temp_dir, f"{uuid.uuid4()}{file_extension}")
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Add processing to background task
    background_tasks.add_task(async_process_file, temp_file_path, table_type)

    return UploadResponse(
        filename=file.filename,
        status="processing",
        message="File uploaded successfully. Ingestion into MySQL and Milvus is running in the background."
    )
