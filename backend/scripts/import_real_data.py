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

def detect_table_type(df: pd.DataFrame, filename: str = "") -> str:
    """
    Automatically detect the table type based on the columns present in the DataFrame.
    """
    columns = set(df.columns)
    
    if "credit_code" in columns or "legal_rep" in columns:
        return "company"
    elif "effective_date" in columns or ("pub_date" in columns and "title" in columns and "project_num" not in columns):
        return "law"
    elif "supplier" in columns or "price" in columns or "product_name" in columns:
        return "product"
    elif "purchaser" in columns and "budget" in columns:
        return "zhaobiao"
    elif "winner" in columns and "win_amount" in columns:
        return "zhongbiao"
    elif "zhaobiao" in filename.lower():
        return "zhaobiao"
    elif "zhongbiao" in filename.lower():
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
        table_type = detect_table_type(df, os.path.basename(file_path))
        if not table_type:
            logger.error(f"Could not automatically detect table type for {file_path}. Missing required signature columns.")
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
                    product_name=clean_string(row.get("product_name")), supplier=clean_string(row.get("supplier")),
                    price=clean_decimal(row.get("price")), unit=clean_string(row.get("unit")),
                    supplier_address=clean_string(row.get("supplier_address")), province=clean_string(row.get("province")),
                    city=clean_string(row.get("city")), county=clean_string(row.get("county")),
                    contact_person=clean_string(row.get("contact_person")), contact_phone=clean_string(row.get("contact_phone")),
                    email=clean_string(row.get("email")), product_params=clean_string(row.get("product_params")),
                    metadata_json=metadata_json
                )
            elif table_type == "zhaobiao":
                obj = Zhaobiao(
                    id=record_id, source=clean_string(row.get("source")),
                    title=clean_string(row.get("title")), project_name=clean_string(row.get("project_name")),
                    project_num=clean_string(row.get("project_num")), purchaser=clean_string(row.get("purchaser")),
                    agency=clean_string(row.get("agency")), budget=clean_decimal(row.get("budget")),
                    stage=clean_string(row.get("stage")), address=clean_string(row.get("address")),
                    content=clean_string(row.get("content")), metadata_json=metadata_json
                )
            elif table_type == "zhongbiao":
                obj = Zhongbiao(
                    id=record_id, source=clean_string(row.get("source")),
                    project_name=clean_string(row.get("project_name")), project_num=clean_string(row.get("project_num")),
                    purchaser=clean_string(row.get("purchaser")), agency=clean_string(row.get("agency")),
                    winner=clean_string(row.get("winner")), win_amount=clean_decimal(row.get("win_amount")),
                    win_date=clean_string(row.get("win_date")), province=clean_string(row.get("province")),
                    city=clean_string(row.get("city")), county=clean_string(row.get("county")),
                    content=clean_string(row.get("content")), metadata_json=metadata_json
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

def process_milvus_file(file_path: str, table_type: str = None):
    logger.info(f"Processing Milvus vector data from {file_path}...")
    try:
        df = read_data_file(file_path)
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return

    if not table_type:
        table_type = detect_table_type(df, os.path.basename(file_path))
        if not table_type:
            logger.error(f"Could not automatically detect table type for {file_path}. Missing required signature columns.")
            return
            
    logger.info(f"Detected table type for Milvus: {table_type}")

    # Initialize LangChain semantic chunker with better overlap and separators for Chinese
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
    )

    milvus_batch = []
    success_chunks = 0
    
    def flush_milvus_batch():
        if not milvus_batch: return
        try:
            texts = [item["chunk_text"] for item in milvus_batch]
            model = get_embedding_model()
            embeddings = model.encode(texts, normalize_embeddings=True).tolist()
            for i, item in enumerate(milvus_batch):
                item["embedding"] = embeddings[i]
            insert_into_milvus(f"milvus_{table_type}", milvus_batch)
            milvus_batch.clear()
        except Exception as e:
            logger.error(f"Milvus flush failed: {e}")
            milvus_batch.clear()

    for index, row in df.iterrows():
        doc_id = clean_string(row.get("id")) or str(uuid.uuid4())
        
        # If 'chunk_text' or 'core_text_for_bge_m3' exists, use it. Otherwise, build it from the row fields.
        if "chunk_text" in row and pd.notnull(row["chunk_text"]):
            raw_text = str(row["chunk_text"])
        elif "core_text_for_bge_m3" in row and pd.notnull(row["core_text_for_bge_m3"]):
            raw_text = str(row["core_text_for_bge_m3"])
        else:
            parts = []
            for col in df.columns:
                if col not in ['id', 'metadata', 'vector'] and pd.notnull(row[col]):
                    parts.append(f"{col}: {row[col]}")
            raw_text = "\n".join(parts)
            if "metadata" in row and pd.notnull(row["metadata"]):
                raw_text += f"\n附加信息：{row['metadata']}"

        # Smart extraction: isolate JSON metadata and core textual content safely
        json_start = raw_text.rfind("{")
        json_end = raw_text.rfind("}")
        split_marker = "附加信息："
        
        metadata = {}
        main_text = raw_text

        # Only extract if it looks like a valid JSON dictionary at the end
        if json_start != -1 and json_end != -1 and json_end > json_start:
            meta_str = raw_text[json_start:json_end+1]
            try:
                metadata = json.loads(meta_str)
                # If json loads successfully, strip it from the main text to prevent redundancy
                if split_marker in raw_text[:json_start]:
                    main_text = raw_text[:raw_text.rfind(split_marker)].strip()
                else:
                    main_text = raw_text[:json_start].strip()
            except Exception:
                # If it's not valid JSON, treat the whole thing as main_text to avoid data loss
                metadata = {}
                main_text = raw_text

        # Augment main text with long fields from metadata if they are missing
        if table_type == "company" and metadata.get("business_scope") and metadata.get("business_scope") not in main_text:
            main_text += "\n经营范围: " + str(metadata.get("business_scope"))
        if table_type == "law" and metadata.get("content") and len(main_text) < 200:
            main_text += "\n正文: " + str(metadata.get("content"))
        if table_type == "product" and metadata.get("product_params") and metadata.get("product_params") not in main_text:
            main_text += "\n产品参数: " + str(metadata.get("product_params"))
        if table_type in ["zhaobiao", "zhongbiao"]:
            for key in ["content", "other_supplements", "specs"]:
                if metadata.get(key) and str(metadata.get(key)) not in main_text:
                    main_text += f"\n{key}: " + str(metadata.get(key))

        # Extract semantic headers to prepend to each chunk
        header_parts = []
        if table_type == "company":
            header_parts.append(f"企业名称: {metadata.get('company_name', '')}")
            header_parts.append(f"法定代表人: {metadata.get('legal_rep', '')}")
            header_parts.append(f"统一社会信用代码: {metadata.get('credit_code', '')}")
        elif table_type == "law":
            header_parts.append(f"法规标题: {metadata.get('title', '')}")
            header_parts.append(f"发布日期: {metadata.get('pub_date', '')}")
        elif table_type == "product":
            header_parts.append(f"产品名称: {metadata.get('product_name', '')}")
            header_parts.append(f"供应商: {metadata.get('supplier', '')}")
        elif table_type == "zhaobiao":
            header_parts.append(f"招标项目: {metadata.get('project_name', metadata.get('title', ''))}")
            header_parts.append(f"采购人: {metadata.get('purchaser', '')}")
        elif table_type == "zhongbiao":
            header_parts.append(f"中标项目: {metadata.get('project_name', metadata.get('title', ''))}")
            header_parts.append(f"中标人: {metadata.get('winner', '')}")
            header_parts.append(f"采购人: {metadata.get('purchaser', '')}")
            
        header_text = " | ".join([p for p in header_parts if p and not p.endswith(": ")])
        if header_text:
            header_text = f"[{header_text}]\n"

        # Split long content into semantic chunks
        chunks = text_splitter.split_text(main_text)
        if not chunks:
            chunks = ["无详细内容"]

        for chunk_idx, chunk_text in enumerate(chunks):
            # Context-aware embedding text: Header + Chunk
            final_text = header_text + f"内容片段:\n{chunk_text}"

            # Prepare metadata JSON based on the table type to support hybrid filtering
            chunk_metadata = {}
            if table_type == "company":
                chunk_metadata["source"] = clean_string(row.get("source")) or ""
            elif table_type == "law":
                chunk_metadata["source"] = clean_string(row.get("source")) or ""
                chunk_metadata["pub_date"] = clean_string(row.get("pub_date")) or metadata.get("pub_date", "")
            elif table_type == "product":
                chunk_metadata["source"] = clean_string(row.get("source")) or ""
            elif table_type == "zhaobiao":
                chunk_metadata["source"] = clean_string(row.get("source")) or ""
                chunk_metadata["category"] = clean_string(row.get("category")) or metadata.get("industry", "")
                chunk_metadata["pub_date"] = clean_string(row.get("pub_date")) or metadata.get("pub_date", "")
                chunk_metadata["purchaser"] = clean_string(row.get("purchaser")) or metadata.get("purchaser", "")
            elif table_type == "zhongbiao":
                chunk_metadata["source"] = clean_string(row.get("source")) or ""
                chunk_metadata["category"] = clean_string(row.get("category")) or metadata.get("industry", "")
                chunk_metadata["pub_date"] = clean_string(row.get("pub_date")) or metadata.get("win_date", "")
                chunk_metadata["purchaser"] = clean_string(row.get("purchaser")) or metadata.get("purchaser", "")

            chunk_data = {
                "id": f"{doc_id}_{chunk_idx}"[:95],
                "doc_id": str(doc_id)[:95],
                "chunk_index": int(chunk_idx),
                "knowledge_base_id": "kb_default",
                "chunk_text": final_text[:65000],
                "metadata": chunk_metadata
            }

            milvus_batch.append(chunk_data)
            success_chunks += 1
            
            if len(milvus_batch) >= 300:
                flush_milvus_batch()
                logger.info(f"Vectorized and inserted {success_chunks} chunks into Milvus...")

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
            
            # strict routing based on prefix
            if lower_name.startswith("mysql_"):
                logger.info(f"Found MySQL target file: {filename}")
                process_mysql_file(file_path, matched_type)
                found_files = True
            elif lower_name.startswith("milvus_"):
                logger.info(f"Found Milvus target file: {filename}")
                process_milvus_file(file_path, matched_type)
                found_files = True
            else:
                logger.info(f"Found generic target file: {filename}, processing for both MySQL and Milvus")
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
