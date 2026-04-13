from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import chat, document
from app.core.config import settings

app = FastAPI(
    title="Bidding RAG System API",
    description="Smart QA System for Bidding, Enterprise, Policy, and Price info",
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
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(document.router, prefix="/api/v1/documents", tags=["Documents"])

@app.get("/")
async def root():
    return {"message": "Welcome to Bidding RAG System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
