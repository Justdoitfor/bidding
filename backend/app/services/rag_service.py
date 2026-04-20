from pymilvus import Collection
from sentence_transformers import SentenceTransformer
from app.rag.vector_store import get_milvus_connection
import logging

logger = logging.getLogger(__name__)

# Global model instance for efficiency
_embed_model = None

def get_embedding_model():
    """Lazy load the BAAI/bge-m3 model to save memory until needed."""
    global _embed_model
    if _embed_model is None:
        logger.info("Loading BAAI/bge-m3 embedding model for retrieval...")
        _embed_model = SentenceTransformer("BAAI/bge-m3")
    return _embed_model

def retrieve_from_milvus(query: str, top_k: int = 5) -> list:
    """
    Search all Phase 1 Milvus collections for the given query.
    Returns a combined list of top_k results.
    """
    try:
        get_milvus_connection()
        model = get_embedding_model()
        
        # Generate embedding for the query
        query_vector = model.encode([query], normalize_embeddings=True).tolist()[0]
        
        collections_to_search = [
            "milvus_company", 
            "milvus_law", 
            "milvus_product", 
            "milvus_zhaobiao", 
            "milvus_zhongbiao"
        ]
        
        search_params = {
            "metric_type": "IP",
            "params": {"ef": 64},
        }
        
        all_results = []
        
        for col_name in collections_to_search:
            try:
                col = Collection(col_name)
                col.load() # Load into memory before searching
                
                # Check schema to see if "source" field exists in this collection
                schema_fields = [f.name for f in col.schema.fields]
                output_fields = ["core_text_for_bge_m3"]
                if "source" in schema_fields:
                    output_fields.append("source")
                
                # We want to retrieve the core text back
                results = col.search(
                    data=[query_vector],
                    anns_field="vector",
                    param=search_params,
                    limit=top_k,
                    expr=None,
                    output_fields=output_fields
                )
                
                # Parse results
                for hits in results:
                    for hit in hits:
                        # hit.entity.get returns the field value
                        text = hit.entity.get("core_text_for_bge_m3")
                        source = hit.entity.get("source") if "source" in output_fields else f"[{col_name}]"
                        score = hit.score
                        
                        all_results.append({
                            "collection": col_name,
                            "text": text,
                            "source": source,
                            "score": score
                        })
            except Exception as e:
                logger.warning(f"Failed to search collection {col_name}: {e}")
                
        # Sort combined results by score descending and take top_k overall
        all_results.sort(key=lambda x: x["score"], reverse=True)
        top_results = all_results[:top_k]
        
        return top_results

    except Exception as e:
        logger.error(f"Error during Milvus retrieval: {e}")
        return []
