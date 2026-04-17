import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app.rag.vector_store import create_milvus_collections, insert_into_milvus

create_milvus_collections()
try:
    insert_into_milvus("milvus_company", [{"id": "1_0", "doc_id": "1", "chunk_index": 0, "core_text_for_bge_m3": "test", "source": "src", "vector": [0.1]*1024}])
except Exception as e:
    print(f"Error: {e}")
