import sys
import os
import logging
from pymilvus import utility

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, engine
from app.models.domain import Base
from app.rag.vector_store import get_milvus_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def clear_milvus():
    try:
        get_milvus_connection()
        collections = utility.list_collections()
        for col in collections:
            utility.drop_collection(col)
            logger.info(f"Dropped Milvus collection: {col}")
    except Exception as e:
        logger.error(f"Error clearing Milvus: {e}")

def clear_mysql():
    db = SessionLocal()
    try:
        # Disable foreign key checks for dropping/truncating
        db.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        tables = ["company", "law", "product", "zhaobiao", "zhongbiao"]
        for table in tables:
            db.execute(f"TRUNCATE TABLE {table};")
            logger.info(f"Truncated MySQL table: {table}")
            
        db.execute("SET FOREIGN_KEY_CHECKS = 1;")
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing MySQL: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting data clearance...")
    clear_milvus()
    clear_mysql()
    logger.info("Data clearance completed!")
