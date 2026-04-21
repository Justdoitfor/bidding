from pymilvus import Collection
from sentence_transformers import SentenceTransformer, CrossEncoder
from app.rag.vector_store import get_milvus_connection
from app.models.database import SessionLocal
from app.models.domain import Company, Law, Product, Zhaobiao, Zhongbiao
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Global model instance for efficiency
_embed_model = None
_reranker_model = None
_collection_cache = {}

def get_embedding_model():
    """Lazy load the BAAI/bge-m3 model to save memory until needed."""
    global _embed_model
    if _embed_model is None:
        logger.info("Loading BAAI/bge-m3 embedding model for retrieval...")
        _embed_model = SentenceTransformer(settings.BGE_M3_MODEL_PATH)
    return _embed_model

def get_reranker_model():
    """Lazy load the Reranker model."""
    global _reranker_model
    if _reranker_model is None:
        logger.info("Loading BAAI/bge-reranker-base model for retrieval reranking...")
        _reranker_model = CrossEncoder("BAAI/bge-reranker-base")
    return _reranker_model

def get_milvus_collection(name: str) -> Collection:
    col = _collection_cache.get(name)
    if col is None:
        col = Collection(name)
        col.load()
        _collection_cache[name] = col
    return col

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
        
        mysql_model_by_collection = {
            "milvus_company": Company,
            "milvus_law": Law,
            "milvus_product": Product,
            "milvus_zhaobiao": Zhaobiao,
            "milvus_zhongbiao": Zhongbiao,
        }
        sources_by_collection_and_doc_id = {}
        db = SessionLocal()
        try:
            for col_name, model_cls in mysql_model_by_collection.items():
                sources_by_collection_and_doc_id[col_name] = {}
        finally:
            db.close()

        def hydrate_sources(results: list) -> None:
            db = SessionLocal()
            try:
                doc_ids_by_collection = {}
                for item in results:
                    doc_ids_by_collection.setdefault(item["collection"], set()).add(item["doc_id"])

                for col_name, doc_ids in doc_ids_by_collection.items():
                    model_cls = mysql_model_by_collection.get(col_name)
                    if not model_cls or not doc_ids:
                        continue
                    rows = db.query(model_cls).filter(model_cls.id.in_(list(doc_ids))).all()
                    sources_by_collection_and_doc_id[col_name] = {r.id: (r.source or "") for r in rows}
            finally:
                db.close()

        for col_name in collections_to_search:
            try:
                col = get_milvus_collection(col_name)
                
                schema_fields = [f.name for f in col.schema.fields]
                if "chunk_text" in schema_fields and "embedding" in schema_fields:
                    anns_field = "embedding"
                    output_fields = ["doc_id", "chunk_text"]
                    if col_name == "milvus_law":
                        for f in ["title", "effective_date", "chapter", "article"]:
                            if f in schema_fields:
                                output_fields.append(f)
                else:
                    # Fallback for older schema (should be removed after full reset)
                    anns_field = "vector"
                    output_fields = ["doc_id", "core_text_for_bge_m3"]
                    if "source" in schema_fields:
                        output_fields.append("source")

                results = col.search(
                    data=[query_vector],
                    anns_field=anns_field,
                    param=search_params,
                    limit=top_k * 3, # Retrieve more candidates for reranking
                    expr=None,
                    output_fields=output_fields
                )
                
                # Parse results
                for hits in results:
                    for hit in hits:
                        if "chunk_text" in output_fields:
                            text = hit.entity.get("chunk_text")
                            doc_id = hit.entity.get("doc_id")
                            extra = {}
                            if col_name == "milvus_law":
                                extra = {
                                    "title": hit.entity.get("title") if "title" in output_fields else None,
                                    "effective_date": hit.entity.get("effective_date") if "effective_date" in output_fields else None,
                                    "chapter": hit.entity.get("chapter") if "chapter" in output_fields else None,
                                    "article": hit.entity.get("article") if "article" in output_fields else None,
                                }
                        else:
                            text = hit.entity.get("core_text_for_bge_m3")
                            doc_id = hit.entity.get("doc_id")
                            extra = {}
                            
                        score = hit.score
                        item = {
                            "collection": col_name,
                            "doc_id": doc_id,
                            "text": text,
                            "score": score,
                        }
                        if extra:
                            item.update(extra)
                        all_results.append(item)
            except Exception as e:
                logger.warning(f"Failed to search collection {col_name}: {e}")
                
        # Reranking with CrossEncoder
        if all_results:
            reranker = get_reranker_model()
            # Prepare pairs for reranking
            sentence_pairs = [[query, item["text"]] for item in all_results]
            rerank_scores = reranker.predict(sentence_pairs)
            
            # Update scores and sort
            for i, item in enumerate(all_results):
                item["rerank_score"] = float(rerank_scores[i])
                
            all_results.sort(key=lambda x: x["rerank_score"], reverse=True)
            
        top_results = all_results[:top_k]

        hydrate_sources(top_results)
        for item in top_results:
            item["source"] = sources_by_collection_and_doc_id.get(item["collection"], {}).get(item["doc_id"], "") or f"[{item['collection']}]"
        
        return top_results

    except Exception as e:
        logger.error(f"Error during Milvus retrieval: {e}")
        return []
