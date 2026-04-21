import pandas as pd
import random
from datetime import datetime, timedelta
import os
import uuid

DATA_DIR = "/workspace/data"
os.makedirs(DATA_DIR, exist_ok=True)

def random_date(start, end):
    return (start + timedelta(days=random.randint(0, int((end - start).days)))).strftime('%Y-%m-%d')

# 1. Company
companies = []
for i in range(1, 101):
    companies.append({
        "id": f"COMP_{i:04d}",
        "source": "MockData",
        "company_name": f"北京科技有限公司{i}",
        "legal_rep": f"张{i}",
        "est_date": random_date(datetime(2010, 1, 1), datetime(2023, 1, 1)),
        "capital": f"{random.randint(100, 10000)}万元",
        "company_type": "有限责任公司",
        "reg_number": f"110100{random.randint(10000000, 99999999)}",
        "taxpayer_id": f"91110100MA{random.randint(1000000, 9999999)}",
        "business_term": "2010-01-01 至 无固定期限",
        "credit_code": f"91110100MA{random.randint(1000000, 9999999)}",
        "status": "存续",
        "address": f"北京市海淀区中关村大街{i}号",
        "province": "北京市",
        "city": "北京市",
        "district": "海淀区",
        "industry": "软件和信息技术服务业",
        "business_scope": "技术开发、技术咨询、技术服务；计算机系统服务；基础软件服务；应用软件服务。",
        "metadata": '{"source": "mock"}'
    })
pd.DataFrame(companies).to_csv(f"{DATA_DIR}/company.csv", index=False)

# 2. Law
laws = []
for i in range(1, 101):
    laws.append({
        "id": f"LAW_{i:04d}",
        "source": "MockData",
        "title": f"中华人民共和国招标投标法实施条例第{i}章",
        "pub_date": random_date(datetime(2015, 1, 1), datetime(2023, 1, 1)),
        "effective_date": random_date(datetime(2015, 1, 1), datetime(2023, 1, 1)),
        "content": f"第{i}条：为了规范招标投标活动，保护国家利益、社会公共利益和招标投标活动当事人的合法权益，提高经济效益，保证项目质量，制定本条例。具体细则参照相关规定执行。这是第{i}条的测试内容。",
        "metadata": '{"type": "regulation"}'
    })
pd.DataFrame(laws).to_csv(f"{DATA_DIR}/law.csv", index=False)

# 3. Product
products = []
for i in range(1, 101):
    products.append({
        "id": f"PROD_{i:04d}",
        "source": "MockData",
        "product_name": f"高性能企业级服务器 Gen{i}",
        "gather_time": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
        "supplier": f"服务器供应商{i}有限公司",
        "price": f"{random.randint(5000, 50000)}.00",
        "supplier_address": f"上海市朝阳区科技园{i}号",
        "province": "上海市",
        "city": "上海市",
        "county": "朝阳区",
        "product_params": f"CPU: 64核, RAM: {random.choice([128, 256, 512])}GB, Storage: 4TB NVMe, 网络: 双万兆",
        "contact_person": f"王{i}",
        "contact_phone": f"1380013{i:04d}",
        "email": f"contact{i}@supplier.com",
        "metadata": '{"category": "hardware"}'
    })
pd.DataFrame(products).to_csv(f"{DATA_DIR}/product.csv", index=False)

# 4. Zhaobiao
zhaobiaos = []
for i in range(1, 101):
    zhaobiaos.append({
        "id": f"ZHAO_{i:04d}",
        "source": "MockData",
        "category": "货物类",
        "stage": "招标公告",
        "title": f"某省政务云平台第{i}期扩容项目招标公告",
        "project_name": f"政务云扩容项目{i}",
        "project_num": f"ZB-2024-{i:04d}",
        "pub_date": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
        "purchaser": f"某省大数据管理中心{i}",
        "agency": f"中招国际招标有限公司{i}分公司",
        "content": f"项目概况：本项目主要采购一批高性能服务器、存储设备及网络安全设备，预算金额为{random.randint(100, 1000)}万元。投标人需具备相关资质，并在截止日期前提交投标文件。",
        "address": f"某省某市某区某路{i}号",
        "budget": f"{random.randint(100, 1000)}0000",
        "metadata": '{"tag": "IT"}'
    })
pd.DataFrame(zhaobiaos).to_csv(f"{DATA_DIR}/zhaobiao.csv", index=False)

# 5. Zhongbiao
zhongbiaos = []
for i in range(1, 101):
    zhongbiaos.append({
        "id": f"ZHONG_{i:04d}",
        "source": "MockData",
        "category": "货物类",
        "title": f"某省政务云平台第{i}期扩容项目中标候选人公示",
        "project_name": f"政务云扩容项目{i}",
        "project_num": f"ZB-2024-{i:04d}",
        "pub_date": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
        "purchaser": f"某省大数据管理中心{i}",
        "agency": f"中招国际招标有限公司{i}分公司",
        "winner": f"北京科技有限公司{i}",
        "win_amount": f"{random.randint(90, 990)}0000",
        "win_date": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
        "address": f"某省某市某区某路{i}号",
        "province": "某省",
        "city": "某市",
        "county": "某区",
        "metadata": '{"status": "completed"}'
    })
pd.DataFrame(zhongbiaos).to_csv(f"{DATA_DIR}/zhongbiao.csv", index=False)

print("Successfully generated 100 mock records for each category.")
