import argparse
import pandas as pd
import json
import sys
import os
import uuid
import math
from sqlalchemy.orm import Session
import logging

# Add backend directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, engine
from app.models.domain import Base, Company, Law, Product, Zhaobiao, Zhongbiao

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def clean_decimal(val):
    if pd.isna(val) or val == "":
        return 0.0
    try:
        # Simple extraction of numbers, you might want more complex regex for '万元' vs '元'
        return float(''.join(c for c in str(val) if c.isdigit() or c == '.'))
    except Exception:
        return 0.0

def clean_string(val):
    if pd.isna(val):
        return None
    return str(val).strip()

def process_file(file_path: str, table_type: str):
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return

    logger.info(f"Loading data from {file_path} for table {table_type}...")
    
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        df = pd.read_excel(file_path)
    elif file_path.endswith(".json"):
        df = pd.read_json(file_path)
    else:
        logger.error("Unsupported file format. Please use .csv, .xlsx, or .json")
        return

    # Replace NaN with None
    df = df.where(pd.notnull(df), None)

    db: Session = next(get_db())
    success_count = 0

    try:
        for index, row in df.iterrows():
            record_id = clean_string(row.get("id")) or str(uuid.uuid4())
            metadata_json = row.to_dict()
            
            # Clean up metadata_json (remove None)
            metadata_json = {k: v for k, v in metadata_json.items() if v is not None}

            if table_type == "company":
                obj = Company(
                    id=record_id,
                    source=clean_string(row.get("source")),
                    company_name=clean_string(row.get("company_name")),
                    legal_rep=clean_string(row.get("legal_rep")),
                    est_date=clean_string(row.get("est_date")),
                    capital=clean_decimal(row.get("capital")),
                    company_type=clean_string(row.get("company_type")),
                    reg_number=clean_string(row.get("reg_number")),
                    taxpayer_id=clean_string(row.get("taxpayer_id")),
                    business_term=clean_string(row.get("business_term")),
                    credit_code=clean_string(row.get("credit_code")),
                    status=clean_string(row.get("status")),
                    address=clean_string(row.get("address")),
                    province=clean_string(row.get("province")),
                    city=clean_string(row.get("city")),
                    district=clean_string(row.get("district")),
                    industry=clean_string(row.get("industry")),
                    insured_count=clean_string(row.get("insured_count")),
                    business_scope=clean_string(row.get("business_scope")),
                    metadata_json=metadata_json
                )
            elif table_type == "law":
                obj = Law(
                    id=record_id,
                    source=clean_string(row.get("source")),
                    title=clean_string(row.get("title")),
                    pub_date=clean_string(row.get("pub_date")),
                    effective_date=clean_string(row.get("effective_date")),
                    content=clean_string(row.get("content")),
                    metadata_json=metadata_json
                )
            elif table_type == "product":
                obj = Product(
                    id=record_id,
                    source=clean_string(row.get("source")),
                    product_name=clean_string(row.get("product_name")),
                    supplier=clean_string(row.get("supplier")),
                    price=clean_decimal(row.get("price")),
                    unit=clean_string(row.get("unit")),
                    supplier_address=clean_string(row.get("supplier_address")),
                    province=clean_string(row.get("province")),
                    city=clean_string(row.get("city")),
                    county=clean_string(row.get("county")),
                    contact_person=clean_string(row.get("contact_person")),
                    contact_phone=clean_string(row.get("contact_phone")),
                    email=clean_string(row.get("email")),
                    product_params=clean_string(row.get("product_params")),
                    metadata_json=metadata_json
                )
            elif table_type == "zhaobiao":
                obj = Zhaobiao(
                    id=record_id,
                    source=clean_string(row.get("source")),
                    title=clean_string(row.get("title")),
                    project_name=clean_string(row.get("project_name")),
                    project_num=clean_string(row.get("project_num")),
                    purchaser=clean_string(row.get("purchaser")),
                    agency=clean_string(row.get("agency")),
                    budget=clean_decimal(row.get("budget")),
                    stage=clean_string(row.get("stage")),
                    address=clean_string(row.get("address")),
                    content=clean_string(row.get("content")),
                    metadata_json=metadata_json
                )
            elif table_type == "zhongbiao":
                obj = Zhongbiao(
                    id=record_id,
                    source=clean_string(row.get("source")),
                    project_name=clean_string(row.get("project_name")),
                    project_num=clean_string(row.get("project_num")),
                    purchaser=clean_string(row.get("purchaser")),
                    agency=clean_string(row.get("agency")),
                    winner=clean_string(row.get("winner")),
                    win_amount=clean_decimal(row.get("win_amount")),
                    win_date=clean_string(row.get("win_date")),
                    province=clean_string(row.get("province")),
                    city=clean_string(row.get("city")),
                    county=clean_string(row.get("county")),
                    content=clean_string(row.get("content")),
                    metadata_json=metadata_json
                )
            else:
                logger.error(f"Unknown table type: {table_type}")
                return

            db.merge(obj)
            success_count += 1
            
            if success_count % 500 == 0:
                db.commit()
                logger.info(f"Inserted {success_count} records...")

        db.commit()
        logger.info(f"Successfully imported {success_count} records into {table_type} table!")
        logger.info(f"TODO: Add Milvus vector embedding logic for {table_type} (e.g. using BGE-M3)")

    except Exception as e:
        db.rollback()
        logger.error(f"Error during import: {e}")

def process_directory(dir_path: str):
    if not os.path.exists(dir_path):
        logger.error(f"Directory not found: {dir_path}")
        return
        
    logger.info(f"Scanning directory: {dir_path} for data files...")
    supported_types = ["company", "law", "product", "zhaobiao", "zhongbiao"]
    found_files = False
    
    for filename in os.listdir(dir_path):
        if filename.startswith("~") or filename.startswith("."):
            continue
            
        lower_name = filename.lower()
        matched_type = None
        
        for t in supported_types:
            if t in lower_name:
                matched_type = t
                break
                
        if matched_type and (lower_name.endswith(".csv") or lower_name.endswith(".xlsx") or lower_name.endswith(".xls") or lower_name.endswith(".json")):
            file_path = os.path.join(dir_path, filename)
            logger.info(f"Found file '{filename}' matching type '{matched_type}'.")
            process_file(file_path, matched_type)
            found_files = True
            
    if not found_files:
        logger.warning(f"No matching data files found in {dir_path}.")
        logger.warning(f"Ensure filenames contain keywords like 'company', 'law', 'product', 'zhaobiao', or 'zhongbiao'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import real data into MySQL/SQLite and Milvus")
    parser.add_argument("--file", type=str, help="Absolute path to the external data file (e.g., D:/data/company.csv)")
    parser.add_argument("--type", type=str, choices=["company", "law", "product", "zhaobiao", "zhongbiao"], help="Target table type")
    parser.add_argument("--dir", type=str, help="Directory containing data files. Auto-matches files based on filename keywords.")
    
    args = parser.parse_args()
    
    if args.dir:
        process_directory(args.dir)
    elif args.file and args.type:
        process_file(args.file, args.type)
    else:
        parser.error("Either --dir must be provided, or both --file and --type must be provided.")
