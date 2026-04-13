from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "招投标信息智能问答平台"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database Settings
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "bidding_db"
    
    # Milvus Vector Database Settings
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_USER: str = ""
    MILVUS_PASSWORD: str = ""
    
    # Redis Cache Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM & Embedding Settings
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    SPARK_API_KEY: str = ""
    SPARK_APP_ID: str = ""
    SPARK_API_SECRET: str = ""
    
    BGE_M3_MODEL_PATH: str = "BAAI/bge-m3"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
