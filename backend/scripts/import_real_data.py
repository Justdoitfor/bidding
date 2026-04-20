import argparse
import pandas as pd
import json
import sys
import os
import uuid
import hashlib
from sqlalchemy.orm import Session
import logging
import re
from sqlalchemy.dialects.mysql import insert as mysql_insert

# Add backend directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, engine
from app.models.domain import Base, Company, Law, Product, Zhaobiao, Zhongbiao
from app.rag.vector_store import create_milvus_collections, insert_into_milvus, drop_milvus_collections, build_milvus_indexes
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure tables and collections are created
Base.metadata.create_all(bind=engine)

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

def iter_data_frames(file_path: str, chunksize: int | None):
    if file_path.endswith(".csv"):
        if chunksize and chunksize > 0:
            for chunk in pd.read_csv(file_path, chunksize=chunksize):
                yield chunk.where(pd.notnull(chunk), None)
            return
        df = pd.read_csv(file_path)
        yield df.where(pd.notnull(df), None)
        return
    if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        df = pd.read_excel(file_path)
        yield df.where(pd.notnull(df), None)
        return
    if file_path.endswith(".json"):
        df = pd.read_json(file_path)
        yield df.where(pd.notnull(df), None)
        return
    raise ValueError("Unsupported file format.")

def normalize_for_hash(val):
    if val is None:
        return None
    if isinstance(val, (int, float, bool)):
        return val
    try:
        s = json.dumps(val, ensure_ascii=False, sort_keys=True)
    except Exception:
        s = str(val)
    if len(s) > 512:
        return hashlib.sha1(s.encode("utf-8")).hexdigest()
    return s

def compute_content_hash(payload: dict) -> str:
    normalized = {k: normalize_for_hash(v) for k, v in payload.items() if k != "content_hash"}
    raw = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

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

def _get_model_by_type(table_type: str):
    if table_type == "company":
        return Company
    if table_type == "law":
        return Law
    if table_type == "product":
        return Product
    if table_type == "zhaobiao":
        return Zhaobiao
    if table_type == "zhongbiao":
        return Zhongbiao
    return None

def _existing_hash_map(db: Session, model, ids: list[str], batch: int = 5000) -> dict[str, str]:
    res: dict[str, str] = {}
    if not ids:
        return res
    for i in range(0, len(ids), batch):
        sub = ids[i:i + batch]
        rows = db.query(model.id, model.content_hash).filter(model.id.in_(sub)).all()
        for rid, h in rows:
            res[str(rid)] = h or ""
    return res

def _bulk_upsert(db: Session, model, rows: list[dict], update_cols: list[str]):
    if not rows:
        return
    stmt = mysql_insert(model.__table__).values(rows)
    update_mapping = {c: getattr(stmt.inserted, c) for c in update_cols}
    stmt = stmt.on_duplicate_key_update(**update_mapping)
    db.execute(stmt)

def process_mysql_file(
    file_path: str,
    table_type: str = None,
    db_session: Session = None,
    mode: str = "full",
    chunksize: int | None = None,
    mysql_batch_size: int = 10000,
):
    logger.info(f"Processing MySQL data from {file_path}...")

    if not table_type:
        table_type = infer_table_type_from_filename(file_path)
        if not table_type:
            logger.error(f"Could not detect table type from filename for {file_path}. Filename must include one of: company/law/product/zhaobiao/zhongbiao")
            return set()

    model = _get_model_by_type(table_type)
    if not model:
        return set()

    db = db_session if db_session else SessionLocal()
    changed_ids: set[str] = set()
    processed = 0

    if table_type == "company":
        update_cols = [
            "content_hash", "source", "company_name", "legal_rep", "est_date", "capital", "company_type",
            "reg_number", "taxpayer_id", "business_term", "credit_code", "status", "address",
            "province", "city", "district", "industry", "insured_count", "business_scope", "metadata_json",
        ]
    elif table_type == "law":
        update_cols = ["content_hash", "source", "title", "pub_date", "effective_date", "content", "metadata_json"]
    elif table_type == "product":
        update_cols = [
            "content_hash", "source", "product_name", "gather_time", "supplier", "price", "supplier_address",
            "province", "city", "county", "product_params", "contact_person", "contact_phone", "email", "metadata_json",
        ]
    elif table_type == "zhaobiao":
        update_cols = [
            "content_hash", "source", "category", "stage", "title", "project_name", "project_num",
            "pub_date", "purchaser", "agency", "content", "address", "budget", "metadata_json",
        ]
    else:
        update_cols = [
            "content_hash", "source", "category", "title", "project_name", "project_num", "pub_date", "purchaser",
            "agency", "winner", "win_amount", "win_date", "address", "province", "city", "county", "metadata_json",
        ]

    try:
        for df in iter_data_frames(file_path, chunksize=chunksize):
            records = df.to_dict(orient="records")
            ids: list[str] = []
            candidate_rows: list[dict] = []

            for rec in records:
                raw_id = clean_string(rec.get("id"))
                record_id = raw_id or str(uuid.uuid4())

                metadata_json = {k: v for k, v in rec.items() if v is not None and k != "metadata"}
                if rec.get("metadata") is not None:
                    try:
                        parsed_meta = json.loads(rec.get("metadata"))
                        if isinstance(parsed_meta, dict):
                            metadata_json.update(parsed_meta)
                        else:
                            metadata_json["raw_metadata"] = rec.get("metadata")
                    except Exception:
                        metadata_json["raw_metadata"] = rec.get("metadata")

                if table_type == "company":
                    row = {
                        "id": record_id,
                        "source": clean_string(rec.get("source")),
                        "company_name": clean_string(rec.get("company_name")),
                        "legal_rep": clean_string(rec.get("legal_rep")),
                        "est_date": clean_string(rec.get("est_date")),
                        "capital": clean_decimal(rec.get("capital")),
                        "company_type": clean_string(rec.get("company_type")),
                        "reg_number": clean_string(rec.get("reg_number")),
                        "taxpayer_id": clean_string(rec.get("taxpayer_id")),
                        "business_term": clean_string(rec.get("business_term")),
                        "credit_code": clean_string(rec.get("credit_code")),
                        "status": clean_string(rec.get("status")),
                        "address": clean_string(rec.get("address")),
                        "province": clean_string(rec.get("province")),
                        "city": clean_string(rec.get("city")),
                        "district": clean_string(rec.get("district")),
                        "industry": clean_string(rec.get("industry")),
                        "insured_count": clean_string(rec.get("insured_count")),
                        "business_scope": clean_string(rec.get("business_scope")),
                        "metadata_json": metadata_json,
                    }
                elif table_type == "law":
                    row = {
                        "id": record_id,
                        "source": clean_string(rec.get("source")),
                        "title": clean_string(rec.get("title")),
                        "pub_date": clean_string(rec.get("pub_date")),
                        "effective_date": clean_string(rec.get("effective_date")),
                        "content": clean_string(rec.get("content")),
                        "metadata_json": metadata_json,
                    }
                elif table_type == "product":
                    row = {
                        "id": record_id,
                        "source": clean_string(rec.get("source")),
                        "product_name": clean_string(rec.get("product_name")),
                        "gather_time": clean_string(rec.get("gather_time")),
                        "supplier": clean_string(rec.get("supplier")),
                        "price": clean_decimal(rec.get("price")),
                        "supplier_address": clean_string(rec.get("supplier_address")),
                        "province": clean_string(rec.get("province")),
                        "city": clean_string(rec.get("city")),
                        "county": clean_string(rec.get("county")),
                        "product_params": clean_string(rec.get("product_params")),
                        "contact_person": clean_string(rec.get("contact_person")),
                        "contact_phone": clean_string(rec.get("contact_phone")),
                        "email": clean_string(rec.get("email")),
                        "metadata_json": metadata_json,
                    }
                elif table_type == "zhaobiao":
                    row = {
                        "id": record_id,
                        "source": clean_string(rec.get("source")),
                        "category": clean_string(rec.get("category")),
                        "stage": clean_string(rec.get("stage")),
                        "title": clean_string(rec.get("title")),
                        "project_name": clean_string(rec.get("project_name")),
                        "project_num": clean_string(rec.get("project_num")),
                        "pub_date": clean_string(rec.get("pub_date")),
                        "purchaser": clean_string(rec.get("purchaser")),
                        "agency": clean_string(rec.get("agency")),
                        "content": clean_string(rec.get("content")),
                        "address": clean_string(rec.get("address")),
                        "budget": clean_decimal(rec.get("budget")),
                        "metadata_json": metadata_json,
                    }
                else:
                    row = {
                        "id": record_id,
                        "source": clean_string(rec.get("source")),
                        "category": clean_string(rec.get("category")),
                        "title": clean_string(rec.get("title")),
                        "project_name": clean_string(rec.get("project_name")),
                        "project_num": clean_string(rec.get("project_num")),
                        "pub_date": clean_string(rec.get("pub_date")),
                        "purchaser": clean_string(rec.get("purchaser")),
                        "agency": clean_string(rec.get("agency")),
                        "winner": clean_string(rec.get("winner")),
                        "win_amount": clean_decimal(rec.get("win_amount")),
                        "win_date": clean_string(rec.get("win_date")),
                        "address": clean_string(rec.get("address")),
                        "province": clean_string(rec.get("province")),
                        "city": clean_string(rec.get("city")),
                        "county": clean_string(rec.get("county")),
                        "metadata_json": metadata_json,
                    }

                row["content_hash"] = compute_content_hash(row)
                ids.append(record_id)
                candidate_rows.append(row)

            if mode == "incremental":
                existing = _existing_hash_map(db, model, ids)
                filtered_rows: list[dict] = []
                for row in candidate_rows:
                    old_hash = existing.get(row["id"])
                    if not old_hash or old_hash != row["content_hash"]:
                        filtered_rows.append(row)
                        changed_ids.add(row["id"])
                candidate_rows = filtered_rows
            else:
                changed_ids.update(ids)

            for i in range(0, len(candidate_rows), mysql_batch_size):
                part = candidate_rows[i:i + mysql_batch_size]
                _bulk_upsert(db, model, part, update_cols=update_cols)
                db.commit()
                processed += len(part)
                if processed and processed % 50000 == 0:
                    logger.info(f"MySQL upserted {processed} records for {table_type}...")

        logger.info(f"Successfully imported {processed} records into MySQL {table_type} table!")
        return changed_ids
    except Exception as e:
        db.rollback()
        logger.error(f"MySQL import error: {e}")
        return changed_ids
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

def process_milvus_file(
    file_path: str,
    table_type: str = None,
    allowed_ids: set[str] | None = None,
    mode: str = "full",
    chunksize: int | None = None,
    milvus_batch_size: int = 2000,
    milvus_flush_every: int = 50000,
):
    logger.info(f"Processing Milvus vector data from {file_path}...")

    if not table_type:
        table_type = infer_table_type_from_filename(file_path)
        if not table_type:
            logger.error(f"Could not detect table type from filename for {file_path}. Filename must include one of: company/law/product/zhaobiao/zhongbiao")
            return 0

    logger.info(f"Detected table type for Milvus: {table_type}")

    model = get_embedding_model()
    milvus_batch: list[dict] = []
    inserted = 0
    inserted_since_flush = 0
    upsert = mode == "incremental"

    def flush_milvus_batch(flush_now: bool):
        nonlocal inserted, inserted_since_flush
        if not milvus_batch:
            return
        try:
            texts = [item["chunk_text"] for item in milvus_batch]
            embeddings = model.encode(texts, normalize_embeddings=True, batch_size=128).tolist()
            for i, item in enumerate(milvus_batch):
                item["embedding"] = embeddings[i]
            insert_into_milvus(f"milvus_{table_type}", milvus_batch, upsert=upsert, flush=flush_now)
            inserted += len(milvus_batch)
            inserted_since_flush += len(milvus_batch)
        except Exception as e:
            logger.error(f"Milvus flush failed: {e}")
        finally:
            milvus_batch.clear()
            if flush_now:
                inserted_since_flush = 0

    text_splitter = None
    if table_type == "law":
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=120,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
        )

    for df in iter_data_frames(file_path, chunksize=chunksize):
        for rec in df.to_dict(orient="records"):
            doc_id = clean_string(rec.get("id")) or str(uuid.uuid4())
            if allowed_ids is not None and doc_id not in allowed_ids:
                continue

            if table_type == "law":
                meta = _parse_metadata_cell(rec.get("metadata"))
                title = clean_string(rec.get("title")) or ""
                effective_date = clean_string(rec.get("effective_date")) or ""
                chapter = clean_string(meta.get("chapter")) or ""
                article = clean_string(meta.get("article")) or ""

                content = clean_string(rec.get("content")) or ""
                if not content:
                    content = title
                chunks = text_splitter.split_text(content) if text_splitter else [content]
                if not chunks:
                    chunks = ["无详细内容"]

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
                    if len(milvus_batch) >= milvus_batch_size:
                        flush_now = inserted_since_flush + len(milvus_batch) >= milvus_flush_every
                        flush_milvus_batch(flush_now=flush_now)
                continue

            if table_type == "company":
                chunk_text = _build_company_chunk(rec)
                milvus_batch.append(
                    {
                        "id": f"{doc_id}_0"[:95],
                        "doc_id": str(doc_id)[:95],
                        "chunk_index": 0,
                        "chunk_text": chunk_text[:65000],
                        "province": (clean_string(rec.get("province")) or "")[:45],
                        "city": (clean_string(rec.get("city")) or "")[:45],
                        "industry": (clean_string(rec.get("industry")) or "")[:95],
                        "status": (clean_string(rec.get("status")) or "")[:45],
                    }
                )
            elif table_type == "product":
                chunk_text = _build_product_chunk(rec)
                milvus_batch.append(
                    {
                        "id": f"{doc_id}_0"[:95],
                        "doc_id": str(doc_id)[:95],
                        "chunk_index": 0,
                        "chunk_text": chunk_text[:65000],
                        "province": (clean_string(rec.get("province")) or "")[:45],
                        "city": (clean_string(rec.get("city")) or "")[:45],
                        "price": float(clean_decimal(rec.get("price"))),
                    }
                )
            elif table_type == "zhaobiao":
                chunk_text = _build_zhaobiao_chunk(rec)
                milvus_batch.append(
                    {
                        "id": f"{doc_id}_0"[:95],
                        "doc_id": str(doc_id)[:95],
                        "chunk_index": 0,
                        "chunk_text": chunk_text[:65000],
                        "address": (clean_string(rec.get("address")) or "")[:250],
                        "category": (clean_string(rec.get("category")) or "")[:95],
                        "budget": float(clean_decimal(rec.get("budget"))),
                        "pub_date": (clean_string(rec.get("pub_date")) or "")[:45],
                    }
                )
            elif table_type == "zhongbiao":
                chunk_text = _build_zhongbiao_chunk(rec)
                meta = _parse_metadata_cell(rec.get("metadata"))
                zhaobiao_doc_id = clean_string(rec.get("zhaobiao_doc_id")) or clean_string(meta.get("zhaobiao_doc_id")) or ""
                milvus_batch.append(
                    {
                        "id": f"{doc_id}_0"[:95],
                        "doc_id": str(doc_id)[:95],
                        "chunk_index": 0,
                        "chunk_text": chunk_text[:65000],
                        "province": (clean_string(rec.get("province")) or "")[:45],
                        "city": (clean_string(rec.get("city")) or "")[:45],
                        "category": (clean_string(rec.get("category")) or "")[:95],
                        "win_amount": float(clean_decimal(rec.get("win_amount"))),
                        "winner": (clean_string(rec.get("winner")) or "")[:250],
                        "purchaser": (clean_string(rec.get("purchaser")) or "")[:250],
                        "zhaobiao_doc_id": str(zhaobiao_doc_id)[:95],
                    }
                )

            if len(milvus_batch) >= milvus_batch_size:
                flush_now = inserted_since_flush + len(milvus_batch) >= milvus_flush_every
                flush_milvus_batch(flush_now=flush_now)

    flush_milvus_batch(flush_now=True)
    logger.info(f"Successfully processed and vectorized {inserted} chunks for milvus_{table_type}!")
    return inserted

def process_directory(
    dir_path: str,
    mode: str,
    mysql_chunksize_company: int,
    mysql_chunksize_other: int,
    mysql_batch_size: int,
    milvus_batch_size: int,
    milvus_flush_every: int,
):
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
                process_mysql_file(
                    file_path,
                    matched_type,
                    mode=mode,
                    chunksize=mysql_chunksize_company if matched_type == "company" else mysql_chunksize_other,
                    mysql_batch_size=mysql_batch_size,
                )
            elif lower_name.startswith("milvus_"):
                logger.info(f"Found Milvus target file: {filename}")
                process_milvus_file(
                    file_path,
                    matched_type,
                    allowed_ids=None,
                    mode=mode,
                    chunksize=mysql_chunksize_company if matched_type == "company" else mysql_chunksize_other,
                    milvus_batch_size=milvus_batch_size,
                    milvus_flush_every=milvus_flush_every,
                )
            else:
                logger.info(f"Found target file: {filename}, processing for both MySQL and Milvus")
                changed_ids = process_mysql_file(
                    file_path,
                    matched_type,
                    mode=mode,
                    chunksize=mysql_chunksize_company if matched_type == "company" else mysql_chunksize_other,
                    mysql_batch_size=mysql_batch_size,
                )
                allowed_ids = changed_ids if mode == "incremental" else None
                process_milvus_file(
                    file_path,
                    matched_type,
                    allowed_ids=allowed_ids,
                    mode=mode,
                    chunksize=mysql_chunksize_company if matched_type == "company" else mysql_chunksize_other,
                    milvus_batch_size=milvus_batch_size,
                    milvus_flush_every=milvus_flush_every,
                )
            found_files = True
            
    if not found_files:
        logger.warning(f"No valid files found. Files must contain a supported type keyword.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, help="Directory containing data files.")
    parser.add_argument("--mode", type=str, choices=["full", "incremental"], default="incremental")
    parser.add_argument("--mysql-chunksize-company", type=int, default=50000)
    parser.add_argument("--mysql-chunksize-other", type=int, default=10000)
    parser.add_argument("--mysql-batch-size", type=int, default=10000)
    parser.add_argument("--milvus-batch-size", type=int, default=2000)
    parser.add_argument("--milvus-flush-every", type=int, default=50000)
    parser.add_argument("--milvus-rebuild-index", action="store_true")
    args = parser.parse_args()
    
    if args.dir:
        milvus_collections = ["milvus_company", "milvus_law", "milvus_product", "milvus_zhaobiao", "milvus_zhongbiao"]
        if args.mode == "full" and args.milvus_rebuild_index:
            try:
                drop_milvus_collections(milvus_collections)
                create_milvus_collections(create_index=False)
            except Exception as e:
                logger.warning(f"Could not reset Milvus collections: {e}")
        else:
            try:
                create_milvus_collections(create_index=True)
            except Exception as e:
                logger.warning(f"Could not connect to Milvus, vector insertion will fail: {e}")

        process_directory(
            args.dir,
            mode=args.mode,
            mysql_chunksize_company=args.mysql_chunksize_company,
            mysql_chunksize_other=args.mysql_chunksize_other,
            mysql_batch_size=args.mysql_batch_size,
            milvus_batch_size=args.milvus_batch_size,
            milvus_flush_every=args.milvus_flush_every,
        )

        if args.mode == "full" and args.milvus_rebuild_index:
            try:
                build_milvus_indexes(milvus_collections)
            except Exception as e:
                logger.warning(f"Milvus build index failed: {e}")
    else:
        parser.error("--dir is required.")
