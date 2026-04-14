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

def create_milvus_collections():
    get_milvus_connection()
    
    # 1. milvus_company
    if not utility.has_collection("milvus_company"):
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="core_text_for_bge_m3", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM)
        ]
        schema = CollectionSchema(fields, description="Company Vector Table")
        col = Collection("milvus_company", schema)
        col.create_index("vector", {"index_type": "HNSW", "metric_type": "IP", "params": {"M": 8, "efConstruction": 64}})
        logger.info("Created collection: milvus_company")
        
    # 2. milvus_law
    if not utility.has_collection("milvus_law"):
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="pub_date", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="core_text_for_bge_m3", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM)
        ]
        schema = CollectionSchema(fields, description="Law Vector Table")
        col = Collection("milvus_law", schema)
        col.create_index("vector", {"index_type": "HNSW", "metric_type": "IP", "params": {"M": 8, "efConstruction": 64}})
        logger.info("Created collection: milvus_law")

    # 3. milvus_product
    if not utility.has_collection("milvus_product"):
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="core_text_for_bge_m3", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM)
        ]
        schema = CollectionSchema(fields, description="Product Vector Table")
        col = Collection("milvus_product", schema)
        col.create_index("vector", {"index_type": "HNSW", "metric_type": "IP", "params": {"M": 8, "efConstruction": 64}})
        logger.info("Created collection: milvus_product")

    # 4. milvus_zhaobiao
    if not utility.has_collection("milvus_zhaobiao"):
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="pub_date", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="purchaser", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="core_text_for_bge_m3", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM)
        ]
        schema = CollectionSchema(fields, description="Zhaobiao Vector Table")
        col = Collection("milvus_zhaobiao", schema)
        col.create_index("vector", {"index_type": "HNSW", "metric_type": "IP", "params": {"M": 8, "efConstruction": 64}})
        logger.info("Created collection: milvus_zhaobiao")

    # 5. milvus_zhongbiao
    if not utility.has_collection("milvus_zhongbiao"):
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="pub_date", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="purchaser", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="core_text_for_bge_m3", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM)
        ]
        schema = CollectionSchema(fields, description="Zhongbiao Vector Table")
        col = Collection("milvus_zhongbiao", schema)
        col.create_index("vector", {"index_type": "HNSW", "metric_type": "IP", "params": {"M": 8, "efConstruction": 64}})
        logger.info("Created collection: milvus_zhongbiao")

def insert_into_milvus(collection_name: str, data: list):
    """
    data should be a list of dictionaries matching the collection schema
    """
    get_milvus_connection()
    col = Collection(collection_name)
    col.insert(data)
    col.flush()
