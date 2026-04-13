from sqlalchemy import create_engine
from app.models.database import Base, engine, SessionLocal
from app.models.domain import Company, Law, Product, Zhaobiao, Zhongbiao, ChatSession, ChatMessage
import uuid
import random
from datetime import datetime, timedelta

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables initialized successfully.")

def generate_fake_data():
    db = SessionLocal()
    try:
        # Check if data already exists to prevent duplication
        if db.query(Company).first():
            print("Fake data already exists. Skipping generation.")
            return

        print("Generating fake data for testing...")

        # 1. Fake Companies
        companies = []
        for i in range(1, 6):
            comp = Company(
                id=f"COMP_{i:04d}",
                source="fake_generator",
                company_name=f"测试企业_{i}号",
                legal_rep=f"法人代表_{i}",
                est_date=(datetime.now() - timedelta(days=random.randint(1000, 5000))).strftime("%Y-%m-%d"),
                capital=round(random.uniform(1000000, 50000000), 2),
                company_type="有限责任公司",
                reg_number=f"REG{random.randint(10000, 99999)}",
                taxpayer_id=f"TAX{random.randint(10000, 99999)}",
                business_term="长期",
                credit_code=f"91110108MA{random.randint(10000, 99999)}",
                status="存续",
                address=f"测试市测试区测试路{i}号",
                province="测试省",
                city="测试市",
                district="测试区",
                industry="高新技术",
                insured_count=str(random.randint(10, 500)),
                business_scope="软件开发；技术服务；信息系统集成",
                metadata_json={"is_fake": True}
            )
            companies.append(comp)
        db.add_all(companies)

        # 2. Fake Laws
        laws = []
        for i in range(1, 4):
            law = Law(
                id=f"LAW_{i:04d}",
                source="fake_generator",
                title=f"《中华人民共和国测试招标投标法实施条例_第{i}部》",
                pub_date=(datetime.now() - timedelta(days=random.randint(100, 500))).strftime("%Y-%m-%d"),
                effective_date=(datetime.now() - timedelta(days=random.randint(10, 50))).strftime("%Y-%m-%d"),
                content=f"这是第{i}部测试法规的正文内容。主要规定了招标投标的各项要求和规范...",
                metadata_json={"is_fake": True}
            )
            laws.append(law)
        db.add_all(laws)

        # 3. Fake Products
        products = []
        for i in range(1, 6):
            prod = Product(
                id=f"PROD_{i:04d}",
                source="fake_generator",
                product_name=f"高性能服务器型号-X{i}",
                supplier=random.choice(companies).company_name,
                price=round(random.uniform(5000, 50000), 2),
                unit="台",
                supplier_address="测试供应商地址",
                province="测试省",
                city="测试市",
                county="测试县",
                contact_person="张采购",
                contact_phone="13800000000",
                email="procure@test.com",
                product_params=f"CPU: 64核, RAM: 256GB, 存储: 4TB NVMe_{i}",
                metadata_json={"is_fake": True}
            )
            products.append(prod)
        db.add_all(products)

        # 4. Fake Zhaobiao
        zhaobiaos = []
        for i in range(1, 6):
            zb = Zhaobiao(
                id=f"ZB_{i:04d}",
                source="fake_generator",
                title=f"关于采购测试系统项目的招标公告_{i}",
                project_name=f"测试系统建设项目_{i}",
                project_num=f"ZB-2024-{i:04d}",
                purchaser=f"某市测试局_{i}",
                agency="某某国际招标有限公司",
                budget=round(random.uniform(100000, 5000000), 2),
                stage="招标公告",
                address="某市招标中心",
                content=f"项目概况：测试系统建设项目_{i}的潜在投标人应在指定地点获取招标文件...",
                metadata_json={"is_fake": True}
            )
            zhaobiaos.append(zb)
        db.add_all(zhaobiaos)

        # 5. Fake Zhongbiao
        zhongbiaos = []
        for i in range(1, 6):
            winner = random.choice(companies).company_name
            zb_ref = zhaobiaos[i-1]
            zb = Zhongbiao(
                id=f"ZHON_{i:04d}",
                source="fake_generator",
                project_name=zb_ref.project_name,
                project_num=zb_ref.project_num,
                purchaser=zb_ref.purchaser,
                agency=zb_ref.agency,
                winner=winner,
                win_amount=round(float(zb_ref.budget) * random.uniform(0.8, 0.98), 2),
                win_date=(datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                province="测试省",
                city="测试市",
                county="测试区",
                content=f"中标候选人公示：第一中标候选人为{winner}，中标金额为...",
                metadata_json={"is_fake": True}
            )
            zhongbiaos.append(zb)
        db.add_all(zhongbiaos)

        db.commit()
        print("Fake data successfully inserted!")

    except Exception as e:
        print(f"Error generating fake data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_fake_data()
