import argparse
import pandas as pd
import json
import sys
import os
import uuid
from sqlalchemy.orm import Session
import logging

# Add backend directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, engine
from app.models.domain import Base, Company, Law, Product, Zhaobiao, Zhongbiao
from app.rag.vector_store import create_milvus_collections, insert_into_milvus
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure tables and collections are created
Base.metadata.create_all(bind=engine)
try:
    create_milvus_collections()
except Exception as e:
    logger.warning(f"Could not connect to Milvus, vector insertion will fail: {e}")

# Load embedding model lazily
_embed_model = None
def get_embedding_model():
    global _embed_model
    if _embed_model is None:
        logger.info("Loading BAAI/bge-m3 embedding model...")
        _embed_model = SentenceTransformer("BAAI/bge-m3")
    return _embed_model

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
        return float(''.join(c for c in str(val) if c.isdigit() or c == '.'))
    except Exception:
        return 0.0

def clean_string(val):
    if pd.isna(val):
        return None
    return str(val).strip()

def read_data_file(file_path: str):
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        df = pd.read_excel(file_path)
    elif file_path.endswith(".json"):
        df = pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file format.")
    return df.where(pd.notnull(df), None)

def infer_table_type_from_filename(file_path: str) -> str:
    filename = os.path.basename(file_path).lower()
    if "company" in filename:
        return "company"
    if "law" in filename:
        return "law"
    if "product" in filename:
        return "product"
    if "zhaobiao" in filename:
        return "zhaobiao"
    if "zhongbiao" in filename:
        return "zhongbiao"
    return None

def process_mysql_file(file_path: str, table_type: str = None, db_session: Session = None):
    logger.info(f"Processing MySQL data from {file_path}...")
    try:
        df = read_data_file(file_path)
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return

    if not table_type:
        table_type = infer_table_type_from_filename(file_path)
        if not table_type:
            logger.error(f"Could not detect table type from filename for {file_path}. Filename must include one of: company/law/product/zhaobiao/zhongbiao")
            return
            
    logger.info(f"Detected table type: {table_type}")

    # Use provided session or create a new one
    db = db_session if db_session else SessionLocal()
    success_count = 0

    try:
        for index, row in df.iterrows():
            record_id = clean_string(row.get("id")) or str(uuid.uuid4())
            
            # Smart metadata parsing
            metadata_json = {k: v for k, v in row.to_dict().items() if v is not None and k != "metadata"}
            if "metadata" in row and pd.notnull(row["metadata"]):
                try:
                    parsed_meta = json.loads(row["metadata"])
                    if isinstance(parsed_meta, dict):
                        metadata_json.update(parsed_meta)
                    else:
                        metadata_json["raw_metadata"] = row["metadata"]
                except Exception:
                    metadata_json["raw_metadata"] = row["metadata"]

            if table_type == "company":
                obj = Company(
                    id=record_id, source=clean_string(row.get("source")),
                    company_name=clean_string(row.get("company_name")), legal_rep=clean_string(row.get("legal_rep")),
                    est_date=clean_string(row.get("est_date")), capital=clean_decimal(row.get("capital")),
                    company_type=clean_string(row.get("company_type")), reg_number=clean_string(row.get("reg_number")),
                    taxpayer_id=clean_string(row.get("taxpayer_id")), business_term=clean_string(row.get("business_term")),
                    credit_code=clean_string(row.get("credit_code")), status=clean_string(row.get("status")),
                    address=clean_string(row.get("address")), province=clean_string(row.get("province")),
                    city=clean_string(row.get("city")), district=clean_string(row.get("district")),
                    industry=clean_string(row.get("industry")), insured_count=clean_string(row.get("insured_count")),
                    business_scope=clean_string(row.get("business_scope")), metadata_json=metadata_json
                )
            elif table_type == "law":
                obj = Law(
                    id=record_id, source=clean_string(row.get("source")),
                    title=clean_string(row.get("title")), pub_date=clean_string(row.get("pub_date")),
                    effective_date=clean_string(row.get("effective_date")), content=clean_string(row.get("content")),
                    metadata_json=metadata_json
                )
            elif table_type == "product":
                obj = Product(
                    id=record_id, source=clean_string(row.get("source")),
                    product_name=clean_string(row.get("product_name")), gather_time=clean_string(row.get("gather_time")),
                    supplier=clean_string(row.get("supplier")), price=clean_decimal(row.get("price")),
                    supplier_address=clean_string(row.get("supplier_address")), province=clean_string(row.get("province")),
                    city=clean_string(row.get("city")), county=clean_string(row.get("county")),
                    contact_person=clean_string(row.get("contact_person")), contact_phone=clean_string(row.get("contact_phone")),
                    email=clean_string(row.get("email")), product_params=clean_string(row.get("product_params")),
                    metadata_json=metadata_json
                )
            elif table_type == "zhaobiao":
                obj = Zhaobiao(
                    id=record_id, source=clean_string(row.get("source")),
                    category=clean_string(row.get("category")), stage=clean_string(row.get("stage")),
                    title=clean_string(row.get("title")), project_name=clean_string(row.get("project_name")),
                    project_num=clean_string(row.get("project_num")), pub_date=clean_string(row.get("pub_date")),
                    purchaser=clean_string(row.get("purchaser")), agency=clean_string(row.get("agency")),
                    content=clean_string(row.get("content")), metadata_json=metadata_json
                )
            elif table_type == "zhongbiao":
                obj = Zhongbiao(
                    id=record_id, source=clean_string(row.get("source")),
                    category=clean_string(row.get("category")), title=clean_string(row.get("title")),
                    project_name=clean_string(row.get("project_name")), project_num=clean_string(row.get("project_num")),
                    pub_date=clean_string(row.get("pub_date")), purchaser=clean_string(row.get("purchaser")),
                    agency=clean_string(row.get("agency")), winner=clean_string(row.get("winner")),
                    win_amount=clean_decimal(row.get("win_amount")), win_date=clean_string(row.get("win_date")),
                    address=clean_string(row.get("address")), province=clean_string(row.get("province")),
                    city=clean_string(row.get("city")), county=clean_string(row.get("county")),
                    metadata_json=metadata_json
                )
            else:
                continue

            db.merge(obj)
            success_count += 1
            if success_count % 500 == 0:
                db.commit()
                logger.info(f"MySQL inserted {success_count} records...")

        db.commit()
        logger.info(f"Successfully imported {success_count} records into MySQL {table_type} table!")
    except Exception as e:
        db.rollback()
        logger.error(f"MySQL import error: {e}")
    finally:
        if not db_session:
            db.close()

def _parse_metadata_cell(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return {}
    if isinstance(val, dict):
        return val
    try:
        parsed = json.loads(str(val))
        if isinstance(parsed, dict):
            return parsed
        return {"raw_metadata": val}
    except Exception:
        return {"raw_metadata": val}

def _build_company_chunk(row: dict) -> str:
    business_scope = clean_string(row.get("business_scope")) or ""
    return (
        f"{clean_string(row.get('company_name')) or ''}，{clean_string(row.get('company_type')) or ''}，"
        f"位于{clean_string(row.get('province')) or ''}{clean_string(row.get('city')) or ''}，"
        f"行业：{clean_string(row.get('industry')) or ''}，状态：{clean_string(row.get('status')) or ''}，"
        f"主营：{business_scope[:100]}"
    )

def _build_product_chunk(row: dict) -> str:
    price = clean_string(row.get("price")) or ""
    return (
        f"产品：{clean_string(row.get('product_name')) or ''}，"
        f"供应商：{clean_string(row.get('supplier')) or ''}，"
        f"价格：{price}，"
        f"地区：{clean_string(row.get('province')) or ''}{clean_string(row.get('city')) or ''}，"
        f"参数：{(clean_string(row.get('product_params')) or '')[:200]}"
    )

def _build_zhaobiao_chunk(row: dict) -> str:
    budget = clean_string(row.get("budget")) or ""
    budget_text = f"预算{budget}万元" if budget and budget != "未知" else ""
    return (
        f"招标公告：{clean_string(row.get('title')) or ''}，"
        f"采购方：{clean_string(row.get('purchaser')) or ''}，代理：{clean_string(row.get('agency')) or ''}，"
        f"{clean_string(row.get('address')) or ''}，{budget_text}，发布：{clean_string(row.get('pub_date')) or ''}"
    )

def _build_zhongbiao_chunk(row: dict) -> str:
    win_amount = clean_string(row.get("win_amount")) or ""
    return (
        f"中标结果：{clean_string(row.get('title')) or ''}，"
        f"中标人：{clean_string(row.get('winner')) or ''}，"
        f"中标金额：{win_amount}，"
        f"采购方：{clean_string(row.get('purchaser')) or ''}，"
        f"地区：{clean_string(row.get('province')) or ''}{clean_string(row.get('city')) or ''}，"
        f"日期：{clean_string(row.get('win_date')) or clean_string(row.get('pub_date')) or ''}"
    )

def process_milvus_file(file_path: str, table_type: str = None):
    logger.info(f"Processing Milvus vector data from {file_path}...")
    try:
        df = read_data_file(file_path)
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return

    if not table_type:
        table_type = infer_table_type_from_filename(file_path)
        if not table_type:
            logger.error(f"Could not detect table type from filename for {file_path}. Filename must include one of: company/law/product/zhaobiao/zhongbiao")
            return

    logger.info(f"Detected table type for Milvus: {table_type}")

    model = get_embedding_model()
    milvus_batch = []
    success_chunks = 0

    def flush_milvus_batch():
        nonlocal success_chunks
        if not milvus_batch:
            return
        try:
            texts = [item["chunk_text"] for item in milvus_batch]
            embeddings = model.encode(texts, normalize_embeddings=True).tolist()
            for i, item in enumerate(milvus_batch):
                item["embedding"] = embeddings[i]
            insert_into_milvus(f"milvus_{table_type}", milvus_batch)
            success_chunks += len(milvus_batch)
        except Exception as e:
            logger.error(f"Milvus flush failed: {e}")
        finally:
            milvus_batch.clear()

    if table_type == "law":
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=120,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
        )

        for _, row in df.iterrows():
            row_dict = row.to_dict()
            doc_id = clean_string(row_dict.get("id")) or str(uuid.uuid4())
            meta = _parse_metadata_cell(row_dict.get("metadata"))
            title = clean_string(row_dict.get("title")) or ""
            effective_date = clean_string(row_dict.get("effective_date")) or ""
            chapter = clean_string(meta.get("chapter")) or ""
            article = clean_string(meta.get("article")) or ""

            content = clean_string(row_dict.get("content")) or ""
            if not content:
                content = title

            chunks = text_splitter.split_text(content) or ["无详细内容"]
            for chunk_idx, chunk_text in enumerate(chunks):
                milvus_batch.append(
                    {
                        "id": f"{doc_id}_{chunk_idx}"[:95],
                        "doc_id": str(doc_id)[:95],
                        "chunk_index": int(chunk_idx),
                        "chunk_text": f"{title}\n{chunk_text}"[:65000],
                        "title": title[:250],
                        "effective_date": effective_date[:45],
                        "chapter": chapter[:250],
                        "article": article[:250],
                    }
                )
                if len(milvus_batch) >= 300:
                    flush_milvus_batch()

        flush_milvus_batch()
        logger.info(f"Successfully processed and vectorized {success_chunks} chunks for milvus_{table_type}!")
        return

    for _, row in df.iterrows():
        row_dict = row.to_dict()
        doc_id = clean_string(row_dict.get("id")) or str(uuid.uuid4())

        if table_type == "company":
            chunk_text = _build_company_chunk(row_dict)
            milvus_batch.append(
                {
                    "id": f"{doc_id}_0"[:95],
                    "doc_id": str(doc_id)[:95],
                    "chunk_index": 0,
                    "chunk_text": chunk_text[:65000],
                    "province": (clean_string(row_dict.get("province")) or "")[:45],
                    "city": (clean_string(row_dict.get("city")) or "")[:45],
                    "industry": (clean_string(row_dict.get("industry")) or "")[:95],
                    "status": (clean_string(row_dict.get("status")) or "")[:45],
                }
            )
        elif table_type == "product":
            chunk_text = _build_product_chunk(row_dict)
            milvus_batch.append(
                {
                    "id": f"{doc_id}_0"[:95],
                    "doc_id": str(doc_id)[:95],
                    "chunk_index": 0,
                    "chunk_text": chunk_text[:65000],
                    "province": (clean_string(row_dict.get("province")) or "")[:45],
                    "city": (clean_string(row_dict.get("city")) or "")[:45],
                    "price": float(clean_decimal(row_dict.get("price"))),
                }
            )
        elif table_type == "zhaobiao":
            chunk_text = _build_zhaobiao_chunk(row_dict)
            milvus_batch.append(
                {
                    "id": f"{doc_id}_0"[:95],
                    "doc_id": str(doc_id)[:95],
                    "chunk_index": 0,
                    "chunk_text": chunk_text[:65000],
                    "address": (clean_string(row_dict.get("address")) or "")[:250],
                    "category": (clean_string(row_dict.get("category")) or "")[:95],
                    "budget": float(clean_decimal(row_dict.get("budget"))),
                    "pub_date": (clean_string(row_dict.get("pub_date")) or "")[:45],
                }
            )
        elif table_type == "zhongbiao":
            chunk_text = _build_zhongbiao_chunk(row_dict)
            meta = _parse_metadata_cell(row_dict.get("metadata"))
            zhaobiao_doc_id = clean_string(row_dict.get("zhaobiao_doc_id")) or clean_string(meta.get("zhaobiao_doc_id")) or ""
            milvus_batch.append(
                {
                    "id": f"{doc_id}_0"[:95],
                    "doc_id": str(doc_id)[:95],
                    "chunk_index": 0,
                    "chunk_text": chunk_text[:65000],
                    "province": (clean_string(row_dict.get("province")) or "")[:45],
                    "city": (clean_string(row_dict.get("city")) or "")[:45],
                    "category": (clean_string(row_dict.get("category")) or "")[:95],
                    "win_amount": float(clean_decimal(row_dict.get("win_amount"))),
                    "winner": (clean_string(row_dict.get("winner")) or "")[:250],
                    "purchaser": (clean_string(row_dict.get("purchaser")) or "")[:250],
                    "zhaobiao_doc_id": str(zhaobiao_doc_id)[:95],
                }
            )
        else:
            continue

        if len(milvus_batch) >= 300:
            flush_milvus_batch()

    flush_milvus_batch()
    logger.info(f"Successfully processed and vectorized {success_chunks} chunks for milvus_{table_type}!")

def process_directory(dir_path: str):
    if not os.path.exists(dir_path):
        logger.error(f"Directory not found: {dir_path}")
        return
        
    logger.info(f"Scanning directory: {dir_path} for data files...")
    supported_types = ["company", "law", "product", "zhaobiao", "zhongbiao"]
    found_files = False
    
    for filename in os.listdir(dir_path):
        if filename.startswith("~") or filename.startswith("."): continue
            
        lower_name = filename.lower()
        matched_type = next((t for t in supported_types if t in lower_name), None)
                
        if matched_type and lower_name.endswith((".csv", ".xlsx", ".xls", ".json")):
            file_path = os.path.join(dir_path, filename)
            
            if lower_name.startswith("mysql_"):
                logger.info(f"Found MySQL target file: {filename}")
                process_mysql_file(file_path, matched_type)
            elif lower_name.startswith("milvus_"):
                logger.info(f"Found Milvus target file: {filename}")
                process_milvus_file(file_path, matched_type)
            else:
                logger.info(f"Found target file: {filename}, processing for both MySQL and Milvus")
                process_mysql_file(file_path, matched_type)
                process_milvus_file(file_path, matched_type)
            found_files = True
            
    if not found_files:
        logger.warning(f"No valid files found. Files must contain a supported type keyword.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, help="Directory containing data files.")
    args = parser.parse_args()
    
    if args.dir:
        process_directory(args.dir)
    else:
        parser.error("--dir is required.")
