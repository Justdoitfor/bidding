from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Since we want a runnable demo without strictly requiring a running MySQL,
# we'll default to SQLite if MySQL fails or isn't available in local run.
# For Docker, it will use MySQL. Let's use a local SQLite for the standalone demo.
SQLALCHEMY_DATABASE_URL = "sqlite:///./bidding_demo.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
