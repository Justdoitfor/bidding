from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import csv
import io
import uuid

from app.models.database import get_db
from app.models.domain import Company, Law, Product, Zhaobiao, Zhongbiao

router = APIRouter()

class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str
    records_inserted: int

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...), 
    table_type: str = Form(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported in this demo.")
        
    content = await file.read()
    text = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(text))
    
    count = 0
    try:
        for row in csv_reader:
            if table_type == "company":
                obj = Company(
                    id=row.get('id', str(uuid.uuid4())),
                    company_name=row.get('company_name', ''),
                    legal_rep=row.get('legal_rep', ''),
                    capital=row.get('capital', 0.0),
                    status=row.get('status', ''),
                    credit_code=row.get('credit_code', '')
                )
            elif table_type == "law":
                obj = Law(id=row.get('id', str(uuid.uuid4())), title=row.get('title', ''), content=row.get('content', ''))
            elif table_type == "product":
                obj = Product(id=row.get('id', str(uuid.uuid4())), product_name=row.get('product_name', ''), price=row.get('price', 0.0))
            elif table_type == "zhaobiao":
                obj = Zhaobiao(id=row.get('id', str(uuid.uuid4())), title=row.get('title', ''), budget=row.get('budget', 0.0))
            elif table_type == "zhongbiao":
                obj = Zhongbiao(id=row.get('id', str(uuid.uuid4())), project_name=row.get('project_name', ''), win_amount=row.get('win_amount', 0.0))
            else:
                raise HTTPException(status_code=400, detail="Unknown table type.")
            
            db.add(obj)
            count += 1
            
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
    return UploadResponse(
        filename=file.filename,
        status="success",
        message="File processed and indexed successfully",
        records_inserted=count
    )
