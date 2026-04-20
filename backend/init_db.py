from app.models.database import Base, engine, SessionLocal
from app.models.domain import Company, Law, Product, Zhaobiao, Zhongbiao, ChatSession, ChatMessage, User
from app.core.security import get_password_hash
import uuid

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables initialized successfully.")

def generate_fake_data():
    db = SessionLocal()
    try:
        print("Generating fake data for testing...")

        if not db.query(User).first():
            admin = User(
                id="admin-uuid-0001",
                username="root",
                password_hash=get_password_hash("admin"),
                is_admin=True,
                is_active=True,
            )
            demo = User(
                id="demo-uuid-0002",
                username="user",
                password_hash=get_password_hash("user123"),
                is_admin=False,
                is_active=True,
            )
            db.add_all([admin, demo])
            db.commit()
        else:
            admin = db.query(User).filter(User.username == "root").first()
            demo = db.query(User).filter(User.username == "user").first()

        if db.query(Company).first():
            print("Business data already exists. Skipping mock business data generation.")
        else:
            print("Database initialized successfully without fake business data.")
            print("Please use the Data Ingestion feature or import_real_data script to load real data.")

        if demo and not db.query(ChatSession).filter(ChatSession.user_id == demo.id).first():
            sid = str(uuid.uuid4())
            db.add(ChatSession(id=sid, user_id=demo.id, title="示例：欢迎使用"))
            db.add(ChatMessage(session_id=sid, role="user", content="你好，系统支持哪些查询？"))
            db.add(ChatMessage(session_id=sid, role="assistant", content="你好！我是招投标信息智能问答助手。你可以向我查询：\n1. 企业工商信息\n2. 招投标公告\n3. 中标公示信息\n4. 产品及价格信息\n5. 相关政策法规\n请随时提问！"))
            db.commit()

        db.commit()
        print("Initialization complete!")

    except Exception as e:
        print(f"Error initializing data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_fake_data()
