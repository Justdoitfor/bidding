from sqlalchemy import create_engine
from app.models.database import Base, engine
from app.models.domain import Company, Law, Product, Zhaobiao, Zhongbiao, ChatSession, ChatMessage

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database initialized successfully.")
