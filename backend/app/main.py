from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routers import chat, document, auth, users
from app.core.config import settings
from app.services.rag_service import get_embedding_model
from app.rag.vector_store import get_milvus_connection
from pymilvus import Collection

from app.core.middlewares import RequestLoggingMiddleware, RateLimitMiddleware
from app.core.exceptions import http_exception_handler, validation_exception_handler, global_exception_handler

app = FastAPI(
    title="招投标信息智能问答平台 API",
    description="招投标、企业、政策法规与价格信息的检索增强智能问答系统",
    version="1.0.0"
)

# Setup Exceptions
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Setup Middlewares
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(document, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(auth, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users, prefix="/api/v1/users", tags=["Users"])

@app.on_event("startup")
def warmup():
    try:
        get_milvus_connection()
    except Exception:
        pass
    try:
        get_embedding_model()
    except Exception:
        pass
    for name in ["milvus_company", "milvus_law", "milvus_product", "milvus_zhaobiao", "milvus_zhongbiao"]:
        try:
            Collection(name).load()
        except Exception:
            pass

@app.get("/")
async def root():
    return {"message": "Welcome to Bidding RAG System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
