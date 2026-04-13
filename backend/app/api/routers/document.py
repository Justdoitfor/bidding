from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

router = APIRouter()

class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    # Stub for document upload
    return UploadResponse(
        filename=file.filename,
        status="success",
        message="File processed and indexed successfully"
    )
