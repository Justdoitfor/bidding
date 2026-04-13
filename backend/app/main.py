from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import chat, document, auth, users
from app.core.config import settings

app = FastAPI(
    title="招投标信息智能问答平台 API",
    description="招投标、企业、政策法规与价格信息的检索增强智能问答系统",
    version="1.0.0"
)

# Setup CORS
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

@app.get("/")
async def root():
    return {"message": "Welcome to Bidding RAG System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
