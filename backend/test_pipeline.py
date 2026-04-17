import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from scripts.import_real_data import process_mysql_file, process_milvus_file
from app.rag.vector_store import create_milvus_collections

create_milvus_collections()
process_mysql_file("../data/company.csv", "company")
process_milvus_file("../data/company.csv", "company")
