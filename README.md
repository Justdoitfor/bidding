# 招标信息智能问答系统 (Bidding RAG System)

本项目是一个基于大语言模型（LLM）与检索增强生成（RAG）技术的智能问答系统，专注于为招标信息、企业信息、政策法规及商品价格等领域提供专业、精准的回答。系统采用了现代化的前后端分离架构，并结合向量检索与关系型数据查询技术，支持企业级的高效信息挖掘与分析。

目前项目已完成 **Phase 1 (MVP)** 开发，具备完整的生产级可用特性。

## 🌟 核心功能特性

- **流式智能问答 (Streaming)**：采用 Server-Sent Events (SSE) 技术，大模型回答呈现打字机效果，大幅降低用户等待焦虑。
- **极简极客 UI 设计**：灵感来源于 Ollama 的极简设计美学，纯灰度主题，内置专业级 Markdown 渲染与紧凑排版。
- **生产级 API 网关**：内置全局异常拦截、滑动窗口限流（基于 Redis，120次/分钟）、全链路请求耗时日志追踪。
- **混合检索增强**：结合 Milvus 的向量语义检索（BGE-M3）与 MySQL 的结构化元数据过滤，提供高精度查询结果。
- **高性能数据入库引擎**：支持全量与增量导入，通过 `content_hash` 实现防重跳过，基于 MySQL 批量 Upsert 与 Milvus 后置索引构建，支持百万级数据的高效吞吐。
- **多模型支持**：无缝对接 Qwen（通义千问）等兼容 OpenAI API 格式的大模型。

---

## 🛠️ 技术栈选型

### 前端 (Frontend)
- 框架：Vue 3 + Composition API
- 语言：TypeScript
- 渲染与解析：Marked + DOMPurify (Markdown 防注入渲染)
- 构建工具：Vite

### 后端 (Backend)
- 框架：FastAPI
- 网关组件：Starlette Middlewares (限流、日志、CORS)
- 包管理：uv (极速依赖管理)

### AI 与数据引擎 (AI & Data)
- 编排框架：LangChain
- 向量数据库：Milvus (PyMilvus)
- Embedding 模型：BGE-M3 (BAAI/bge-m3)
- 关系型数据库：MySQL 8.0
- 缓存与限流：Redis 7

### 部署与运维 (DevOps)
- 容器化：Docker + Docker Compose

---

## 📁 目录结构

```text
bidding/
├── data/               # 真实业务示例数据存放目录 (CSV 格式)
├── frontend/           # Vue 3 前端工程目录
├── backend/            # FastAPI 后端工程目录
│   ├── app/            # 核心业务代码 (API, Models, RAG, Services, Middlewares)
│   ├── scripts/        # 运维与数据脚本
│   │   ├── init_prod.sh        # 生产级一键初始化脚本 (推荐)
│   │   ├── reset_db.py         # 清理数据库
│   │   └── import_real_data.py # 高性能业务数据入库脚本
│   └── pyproject.toml  # uv 依赖管理配置文件
├── architecture/       # 架构设计与方案文档
├── DESIGN.md           # UI/UX 设计规范说明
└── docker-compose.dev.yml # 容器编排文件
```

---

## 🚀 快速启动与初始化

本项目强烈推荐使用纯 Docker 方式进行日常开发与部署，开箱即用。

### 1. 启动所有容器
确保您已安装 Docker Desktop，然后在项目根目录执行：

```bash
# 拉取最新代码并以后台模式构建启动所有容器
docker-compose -f docker-compose.dev.yml up -d --build
```
> **注意 (Windows 用户)**：如果您在 `.env` 或系统环境变量中设置了 `EXTERNAL_DATA_DIR` 为绝对路径（如 `E:\data`），请确保将其修改为 `/e/data` 格式，以避免 Docker Compose 卷挂载路径解析错误。若不设置，默认映射当前目录下的 `./data`。

### 2. 执行生产级一键初始化
容器启动后，执行以下命令即可完成：**数据库清理** -> **默认账号创建** -> **100条真实业务数据全量入库与向量索引构建**。

```bash
# 处理可能存在的 Windows/Linux 换行符问题并执行初始化脚本
docker-compose -f docker-compose.dev.yml exec backend bash -c "sed -i 's/\r$//' scripts/init_prod.sh && bash scripts/init_prod.sh"
```
*注：该脚本会自动读取映射到容器内 `/data` 目录下的 `company.csv`, `law.csv`, `product.csv`, `zhaobiao.csv`, `zhongbiao.csv` 文件。*

### 3. 服务访问
初始化完成后，您可以通过以下地址访问系统：

- **智能问答前台**：`http://localhost:5173/login`
- **管理员后台**：`http://localhost:5173/admin/login`
- **Swagger API 文档**：`http://localhost:8000/docs`

> **默认测试账号**：
> - 管理员：`root` / `admin`
> - 普通用户：`user` / `user123`

---

## 💾 高性能海量数据入库指南

当您需要导入百万级数据时，推荐使用细粒度参数控制内存和 CPU，避免机器 OOM。

**全量导入（首次导入，自动重建索引加速）**
```bash
docker-compose -f docker-compose.dev.yml exec backend uv run python scripts/import_real_data.py \
  --dir /data \
  --mode full \
  --milvus-rebuild-index \
  --mysql-chunksize-company 50000 \
  --mysql-chunksize-other 10000 \
  --mysql-batch-size 10000 \
  --milvus-batch-size 2000 \
  --milvus-flush-every 50000
```

**增量导入（基于 content_hash 自动跳过未变更数据）**
```bash
docker-compose -f docker-compose.dev.yml exec backend uv run python scripts/import_real_data.py \
  --dir /data \
  --mode incremental \
  --mysql-chunksize-company 50000 \
  --mysql-chunksize-other 10000 \
  --mysql-batch-size 10000 \
  --milvus-batch-size 2000 \
  --milvus-flush-every 20000
```

> **低配机器 (如 8C16G) 极限保命参数**：
> 在命令前加上环境变量 `-e OMP_NUM_THREADS=4 -e MKL_NUM_THREADS=4` 限制 PyTorch 核心数，并将所有 `chunksize` 缩小到 `2000`，`batch-size` 缩小到 `200` 以极低内存模式运行。

---

## 👥 团队协作规范

1. **分支管理**：所有的开发工作均在 `dev` 分支进行，确认无误后通过 PR 合并至 `main` 分支。
2. **依赖管理**：后端必须使用 `uv add <package>` 添加依赖，禁止直接使用 `pip`。
3. **接口契约**：前后端联调需以 FastAPI 生成的 Swagger 文档为准。
4. **架构了解**：详细的系统架构、RAG 查询链路与分阶段计划，请参考 `architecture/architecture.md`。
