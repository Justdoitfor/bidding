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

def async_process_file(file_path: str):
    logger.info(f"Background task started for {file_path} (auto-detecting type)")
    try:
        # Process structural data to MySQL (Upsert) - Auto detects table type
        process_mysql_file(file_path)
        # Process unstructured data to Milvus (Semantic Chunking & Embedding) - Auto detects table type
        process_milvus_file(file_path)
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
    file: UploadFile = File(...)
):
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx') or file.filename.endswith('.json')):
        raise HTTPException(status_code=400, detail="Only CSV, XLSX, and JSON files are supported.")

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
    background_tasks.add_task(async_process_file, temp_file_path)

    return UploadResponse(
        filename=file.filename,
        status="processing",
        message="File uploaded successfully. System will automatically detect the data type and ingest it into MySQL and Milvus."
    )
