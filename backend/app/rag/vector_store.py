from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Define Milvus vector dimension based on BGE-M3 (1024 dimension)
VECTOR_DIM = 1024

def get_milvus_connection():
    connections.connect(
        alias="default", 
        host=settings.MILVUS_HOST, 
        port=settings.MILVUS_PORT
    )

def _get_unified_fields():
    """
    Returns the unified Milvus schema as defined in the architecture:
    id, doc_id, chunk_index, knowledge_base_id, chunk_text, metadata (JSON), embedding
    """
    return [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
        FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="chunk_index", dtype=DataType.INT64),
        FieldSchema(name="knowledge_base_id", dtype=DataType.VARCHAR, max_length=50, default_value="kb_default"),
        FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="metadata", dtype=DataType.JSON),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM)
    ]

def create_milvus_collections():
    get_milvus_connection()
    
    # 1. milvus_company
    if not utility.has_collection("milvus_company"):
        schema = CollectionSchema(_get_unified_fields(), description="Company Vector Table")
        col = Collection("milvus_company", schema)
        col.create_index("embedding", {"index_type": "HNSW", "metric_type": "IP", "params": {"M": 8, "efConstruction": 64}})
        logger.info("Created collection: milvus_company")
        
    # 2. milvus_law
    if not utility.has_collection("milvus_law"):
        schema = CollectionSchema(_get_unified_fields(), description="Law Vector Table")
        col = Collection("milvus_law", schema)
        col.create_index("embedding", {"index_type": "HNSW", "metric_type": "IP", "params": {"M": 8, "efConstruction": 64}})
        logger.info("Created collection: milvus_law")

    # 3. milvus_product
    if not utility.has_collection("milvus_product"):
        schema = CollectionSchema(_get_unified_fields(), description="Product Vector Table")
        col = Collection("milvus_product", schema)
        col.create_index("embedding", {"index_type": "HNSW", "metric_type": "IP", "params": {"M": 8, "efConstruction": 64}})
        logger.info("Created collection: milvus_product")

    # 4. milvus_zhaobiao
    if not utility.has_collection("milvus_zhaobiao"):
        schema = CollectionSchema(_get_unified_fields(), description="Zhaobiao Vector Table")
        col = Collection("milvus_zhaobiao", schema)
        col.create_index("embedding", {"index_type": "HNSW", "metric_type": "IP", "params": {"M": 8, "efConstruction": 64}})
        logger.info("Created collection: milvus_zhaobiao")

    # 5. milvus_zhongbiao
    if not utility.has_collection("milvus_zhongbiao"):
        schema = CollectionSchema(_get_unified_fields(), description="Zhongbiao Vector Table")
        col = Collection("milvus_zhongbiao", schema)
        col.create_index("embedding", {"index_type": "HNSW", "metric_type": "IP", "params": {"M": 8, "efConstruction": 64}})
        logger.info("Created collection: milvus_zhongbiao")

def insert_into_milvus(collection_name: str, data: list):
    """
    data should be a list of dictionaries matching the collection schema.
    This function performs an upsert: deletes existing chunks for the given doc_ids, then inserts.
    """
    get_milvus_connection()
    col = Collection(collection_name)
    
    # Extract unique doc_ids from the batch to delete existing chunks
    doc_ids = list(set([item["doc_id"] for item in data if "doc_id" in item]))
    if doc_ids:
        # Construct an IN expression for doc_ids
        # Using string formatting carefully since doc_ids are strings
        in_expr = ", ".join([f"'{d}'" for d in doc_ids])
        delete_expr = f"doc_id in [{in_expr}]"
        try:
            col.delete(expr=delete_expr)
            logger.info(f"Deleted existing vectors for {len(doc_ids)} docs in {collection_name}")
        except Exception as e:
            logger.warning(f"Delete before insert failed (might be empty collection): {e}")

    col.insert(data)
    col.flush()
