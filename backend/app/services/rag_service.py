from app.core.config import settings
from sentence_transformers import SentenceTransformer
from pymilvus import Collection, connections
import logging

logger = logging.getLogger(__name__)

# Cache for embedding model and milvus collections
_embed_model = None
_COLLECTIONS = {}

def get_embedding_model():
    global _embed_model
    if _embed_model is None:
        logger.info("Loading BAAI/bge-m3 embedding model for retrieval...")
        _embed_model = SentenceTransformer(settings.BGE_M3_MODEL_PATH)
    return _embed_model

def get_milvus_collection(name: str) -> Collection:
    if not connections.has_connection("default"):
        connections.connect(alias="default", host=settings.MILVUS_HOST, port=settings.MILVUS_PORT)
    
    if name not in _COLLECTIONS:
        try:
            col = Collection(name)
            col.load()
            _COLLECTIONS[name] = col
        except Exception as e:
            logger.warning(f"Failed to load collection {name}: {e}")
            return None
    return _COLLECTIONS[name]

def retrieve_from_milvus(query: str, top_k: int = 3):
    """
    Search all Phase 1 Milvus collections for the given query.
    Returns a list of dictionaries with text, score, and source metadata.
    """
    model = get_embedding_model()
    # BGE-M3 expects list of strings
    query_embedding = model.encode([query], normalize_embeddings=True)[0].tolist()
    
    search_params = {
        "metric_type": "IP",
        "params": {"ef": 64}
    }
    
    collections_to_search = [
        "milvus_company", "milvus_law", "milvus_product", 
        "milvus_zhaobiao", "milvus_zhongbiao"
    ]
    
    all_results = []
    
    for col_name in collections_to_search:
        col = get_milvus_collection(col_name)
        if not col:
            continue
            
        try:
            # We want to retrieve 'core_text_for_bge_m3' and 'source'
            output_fields = ["core_text_for_bge_m3", "source"]
            # If the collection has 'pub_date' or 'category', we could retrieve them too, 
            # but to keep it uniform across all 5, we just grab core text and source.
            
            results = col.search(
                data=[query_embedding],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                output_fields=output_fields
            )
            
            for hits in results:
                for hit in hits:
                    all_results.append({
                        "collection": col_name,
                        "score": hit.score,
                        "text": hit.entity.get("core_text_for_bge_m3"),
                        "source": hit.entity.get("source") or "未知来源"
                    })
        except Exception as e:
            logger.error(f"Error searching in {col_name}: {e}")
            
    # Sort all results by score descending and keep top_k overall
    all_results.sort(key=lambda x: x["score"], reverse=True)
    return all_results[:top_k]
