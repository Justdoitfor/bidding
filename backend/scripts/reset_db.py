import os
import sys

# Add backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.models.database import Base
# IMPORTANT: Import all models so they are registered with Base.metadata before drop_all/create_all
from app.models.domain import User, Company, Law, Product, Zhaobiao, Zhongbiao, ChatSession, ChatMessage
from app.core.config import settings
from pymilvus import connections, utility

def reset_mysql():
    print("Resetting MySQL database...")
    # Construct the database URL using the individual settings
    database_url = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
    engine = create_engine(database_url)
    # Drop all tables and recreate them to match the latest schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("MySQL tables dropped and recreated successfully.")

def reset_milvus():
    print("Resetting Milvus collections...")
    connections.connect(
        alias="default", 
        host=settings.MILVUS_HOST, 
        port=settings.MILVUS_PORT
    )
    
    collections = [
        "milvus_company", 
        "milvus_law", 
        "milvus_product", 
        "milvus_zhaobiao", 
        "milvus_zhongbiao"
    ]
    
    for col in collections:
        if utility.has_collection(col):
            utility.drop_collection(col)
            print(f"Dropped collection: {col}")
        else:
            print(f"Collection {col} does not exist, skipping.")
            
    print("Milvus collections reset successfully. They will be recreated upon next ingestion.")

if __name__ == "__main__":
    reset_mysql()
    reset_milvus()
    print("\n--- Database Reset Complete ---")
