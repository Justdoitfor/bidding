# 招标信息智能问答系统 - 架构设计与开发规范

## 一、 系统架构设计

系统基于大模型（LLM）与检索增强生成（RAG）技术构建，分为表现层、业务逻辑层、大模型及RAG引擎层、数据存储层。

### 1.1 技术栈总览
- **前端**：Vue 3 + TypeScript + Element Plus + Pinia + Vite
- **后端**：FastAPI + Pydantic
- **AI 引擎**：LangChain / LlamaIndex
- **大模型**：Qwen（本地 vLLM 部署 / API调用） / 讯飞星火（API）
- **向量数据库**：Milvus
- **Embedding 模型**：BGE-M3（支持多语言与长文本）
- **关系型数据库**：MySQL 8.0（存储结构化业务数据）
- **缓存引擎**：Redis（会话管理、高频查询缓存、任务队列）
- **文档解析**：BeautifulSoup（HTML）、PyPDF2（PDF）、Tesseract OCR（图片/扫描件）
- **部署与包管理**：Docker / Docker Compose，`uv` 作为 Python 依赖管理工具。

### 1.2 核心模块交互流程
1. **多路数据解析与入库**：非结构化文件（PDF/HTML）经解析与 OCR 提取文本，通过 Text Splitter 切块，由 BGE-M3 转换为向量，存入 Milvus；提取出的元数据（如项目名称、企业名称、金额）结构化后存入 MySQL。
2. **意图识别与 Agent 路由**：用户输入问题，Agent 先通过 LLM 进行意图识别，判断是【招标信息】、【企业信息】、【政策】还是【价格信息】查询。
3. **混合检索 (Hybrid Search)**：结合 Milvus 的语义检索和 MySQL 的结构化条件过滤（如时间范围、金额区间）。
4. **大模型生成**：检索出的 Context 和用户 Query 组装为 Prompt，调用 Qwen/星火大模型生成专业回复。

---

## 二、 数据组织与处理策略 (数据基座)

目前数据尚未处理，建议按照以下策略进行数据组织与 Pipeline 建设：

### 2.1 招标信息 (Bidding Info)
- **非结构化数据**：招标公告、招标文件、中标公示原文。切块（Chunking）大小建议 500-800 Tokens，保存至 Milvus，添加 `doc_id` 和 `type` 标签。
- **结构化元数据 (MySQL)**：通过大模型或正则抽取关键字段：`项目编号`、`项目名称`、`招标人`、`中标人`、`中标金额`、`发布时间`。
- **查询策略**：采用 Metadata Filtering + 向量检索。例如“2023年北京的医疗项目”，先在 Milvus 中通过 Metadata 过滤时间与地点，再进行语义匹配。

### 2.2 企业信息 (Enterprise Info)
- **结构化数据主导 (MySQL)**：工商信息、资质等级、历史中标记录。建立企业实体表（`companies`）与资质表（`certificates`）。
- **图/关系查询（进阶参考）**：如果涉及企业股权穿透、围标串标分析，建议引入图数据库（Neo4j），当前可先通过 MySQL 外键/联表实现。

### 2.3 政策信息 (Policy Info)
- **纯非结构化**：招投标法、地方政府采购政策。
- **查询策略**：由于政策条文较长，建议采用**层级检索 (Hierarchical Retrieval)** 或 **父子文档检索 (Parent-Child Retriever)**。将条款切分为小块（Child）进行匹配，将整段（Parent）喂给大模型以保证上下文完整。

### 2.4 商品/价格信息 (Product & Price Info)
- **结构化数据主导 (MySQL/Redis)**：商品分类、历史中标单价、供应商报价。
- **查询策略**：Text-to-SQL 或基于大模型的结构化数据查询Agent。用户问“某型号服务器历史中标均价”，Agent 将自然语言转为 SQL，从 MySQL 聚合数据并回答。

---

## 三、 团队协作开发模式与基座架构

本项目为团队协作项目，代码采用标准的**前后端分离**架构，并遵循以下规范。

### 3.1 目录结构划分
- `/frontend`: 前端 Vue 3 工程，由前端团队负责。
- `/backend`: 后端 FastAPI + RAG 工程，由算法与后端团队负责。
- `/docs`: 项目设计、API 接口文档与运维文档。

### 3.2 依赖管理规范
- **后端**：使用 `uv` 进行极速依赖管理。任何新引入的包需通过 `uv add <package>` 执行，并提交 `pyproject.toml` 和 `uv.lock`，严禁直接使用 `pip install` 而不记录。
- **前端**：统一使用 `npm` (或 `pnpm`) 进行管理，提交 `package.json` 与 `package-lock.json`。

### 3.3 Git 协作流 (Git Flow)
1. **主分支**：`main` 为生产环境稳定代码，`develop` 为测试环境代码。
2. **特性分支**：开发新功能请基于 `develop` 检出 `feature/<姓名拼音>-<功能名>` 分支（如 `feature/zhangsan-rag-agent`）。
3. **提交规范 (Commit Message)**：
   - `feat:` 新增功能
   - `fix:` 修复 Bug
   - `docs:` 文档更新
   - `refactor:` 代码重构
   - `chore:` 架构/配置变动

### 3.4 API 交互契约
后端提供 Swagger 文档 (启动后访问 `http://localhost:8000/docs`)。前端通过 `src/api` 下的 Axios 实例统一封装请求，前后端联调前必须先在文档/Swagger中确认接口格式。
