import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, engine
from app.models.domain import Base, Company, Law, Product, Zhaobiao, Zhongbiao
from pymilvus import connections, utility

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_all_data():
    # Clear MySQL tables
    db = SessionLocal()
    try:
        logger.info("Clearing MySQL tables...")
        db.query(Company).delete()
        db.query(Law).delete()
        db.query(Product).delete()
        db.query(Zhaobiao).delete()
        db.query(Zhongbiao).delete()
        db.commit()
        logger.info("MySQL tables cleared.")
    except Exception as e:
        logger.error(f"Failed to clear MySQL: {e}")
        db.rollback()
    finally:
        db.close()

    # Clear Milvus collections
    try:
        logger.info("Clearing Milvus collections...")
        from app.core.config import settings
        connections.connect("default", host=settings.MILVUS_HOST, port=settings.MILVUS_PORT)
        collections = ["milvus_company", "milvus_law", "milvus_product", "milvus_zhaobiao", "milvus_zhongbiao"]
        for col_name in collections:
            if utility.has_collection(col_name):
                utility.drop_collection(col_name)
                logger.info(f"Dropped Milvus collection: {col_name}")
    except Exception as e:
        logger.error(f"Failed to clear Milvus: {e}")

if __name__ == "__main__":
    clear_all_data()
