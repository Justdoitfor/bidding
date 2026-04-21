from sqlalchemy import Column, String, Text, DECIMAL, JSON, Integer, DateTime, Boolean
from app.models.database import Base
from datetime import datetime

class Tenant(Base):
    __tablename__ = "tenant"
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "user"
    id = Column(String(50), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    tenant_id = Column(String(50), index=True, nullable=True) # Phase 2 Multi-tenant
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    id = Column(String(50), primary_key=True, index=True)
    tenant_id = Column(String(50), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "document"
    id = Column(String(50), primary_key=True, index=True)
    kb_id = Column(String(50), index=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), default="processing") # uploaded, processing, success, failed
    file_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class Company(Base):
    __tablename__ = "mysql_company"
    id = Column(String(50), primary_key=True, index=True)
    content_hash = Column(String(64), index=True)
    source = Column(String(255))
    company_name = Column(String(255), index=True)
    legal_rep = Column(String(100))
    est_date = Column(String(50))
    capital = Column(DECIMAL(20, 2))
    company_type = Column(String(100))
    reg_number = Column(String(100))
    taxpayer_id = Column(String(100))
    business_term = Column(String(100))
    credit_code = Column(String(100), unique=True, index=True)
    status = Column(String(50))
    address = Column(String(255))
    province = Column(String(50))
    city = Column(String(50))
    district = Column(String(50))
    industry = Column(String(100))
    insured_count = Column(String(50))
    business_scope = Column(Text)
    metadata_json = Column(JSON)

class Law(Base):
    __tablename__ = "mysql_law"
    id = Column(String(50), primary_key=True, index=True)
    content_hash = Column(String(64), index=True)
    source = Column(String(255))
    title = Column(String(255), index=True)
    pub_date = Column(String(50))
    effective_date = Column(String(50))
    content = Column(Text)
    metadata_json = Column(JSON)

class Product(Base):
    __tablename__ = "mysql_product"
    id = Column(String(50), primary_key=True, index=True)
    content_hash = Column(String(64), index=True)
    source = Column(String(255))
    product_name = Column(String(255), index=True)
    gather_time = Column(String(50))
    supplier = Column(String(255))
    price = Column(DECIMAL(20, 2))
    supplier_address = Column(String(255))
    province = Column(String(50))
    city = Column(String(50))
    county = Column(String(50))
    product_params = Column(Text)
    contact_person = Column(String(100))
    contact_phone = Column(String(50))
    email = Column(String(100))
    metadata_json = Column(JSON)

class Zhaobiao(Base):
    __tablename__ = "mysql_zhaobiao"
    id = Column(String(50), primary_key=True, index=True)
    content_hash = Column(String(64), index=True)
    source = Column(String(255))
    category = Column(String(100))
    stage = Column(String(50))
    title = Column(String(255), index=True)
    project_name = Column(String(255), index=True)
    project_num = Column(String(100), index=True)
    pub_date = Column(String(50))
    purchaser = Column(String(255))
    agency = Column(String(255))
    content = Column(Text)
    address = Column(String(255))
    budget = Column(DECIMAL(20, 2))
    metadata_json = Column(JSON)

class Zhongbiao(Base):
    __tablename__ = "mysql_zhongbiao"
    id = Column(String(50), primary_key=True, index=True)
    content_hash = Column(String(64), index=True)
    source = Column(String(255))
    category = Column(String(100))
    title = Column(String(255), index=True)
    project_name = Column(String(255), index=True)
    project_num = Column(String(100), index=True)
    pub_date = Column(String(50))
    purchaser = Column(String(255))
    agency = Column(String(255))
    winner = Column(String(255), index=True)
    win_amount = Column(DECIMAL(20, 2))
    win_date = Column(String(50))
    address = Column(String(255))
    province = Column(String(50))
    city = Column(String(50))
    county = Column(String(50))
    metadata_json = Column(JSON)

class ChatSession(Base):
    __tablename__ = "chat_session"
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), index=True)
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_message"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(50), index=True)
    role = Column(String(20)) # "user" or "assistant"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
