# 招标信息智能问答系统 (Bidding RAG System)

本项目是一个基于大语言模型（LLM）与检索增强生成（RAG）技术的智能问答系统，专注于为招标信息、企业信息、政策法规及商品价格等领域提供专业、精准的回答。系统采用了现代化的前后端分离架构，并结合向量检索与关系型数据查询技术，支持企业级的高效信息挖掘与分析。

## 🌟 核心功能特性

- **智能问答界面 (Demo)**：包含前端对话系统，支持企业、招标、中标等数据的问答交互。
- **后台管理系统 (Demo)**：支持查看用户问答历史记录，以及直接在前端上传CSV文件更新知识库。
- **多模态文档解析**：支持 HTML、PDF、扫描件/图片的自动化解析与信息抽取。
- **混合检索增强**：结合 Milvus 的向量语义检索与 MySQL 的结构化条件过滤，提供高精度查询结果。
- **多模型支持**：无缝对接 Qwen（本地 vLLM 或 API）及讯飞星火（API）。
- **极速依赖管理**：后端采用 `uv` 工具，实现 Python 虚拟环境与依赖的秒级构建。

---

## 🛠️ 技术栈选型

### 前端 (Frontend)
- 框架：Vue 3 + Composition API
- 语言：TypeScript
- UI 组件库：Element Plus
- 状态管理：Pinia
- 构建工具：Vite

### 后端 (Backend)
- 框架：FastAPI
- 异步支持：Uvicorn, aiohttp, aiomysql
- 包管理：uv

### AI 与数据引擎 (AI & Data)
- 编排框架：LangChain / LlamaIndex
- 向量数据库：Milvus (PyMilvus)
- Embedding 模型：BGE-M3 (BAAI/bge-m3)
- 关系型数据库：MySQL 8.0 (Demo模式默认使用 SQLite 以便快速启动)
- 缓存与消息：Redis

### 部署与运维 (DevOps)
- 容器化：Docker + Docker Compose

---

## 📁 目录结构

```text
bidding-rag-system/
├── data/               # 数据库设计文档及示例数据
│   ├── 数据库文档.md    # 数据表设计规范
│   └── sample_company.csv # 示例导入数据
├── frontend/           # Vue 3 前端工程目录
│   ├── src/            # 前端源码 (api, components, views, store 等)
│   ├── package.json    # npm 依赖配置
│   └── Dockerfile      # 前端构建镜像
├── backend/            # FastAPI 后端工程目录
│   ├── app/            # 核心业务代码
│   │   ├── api/        # 路由层 (RESTful API)
│   │   ├── core/       # 核心配置 (Config, Security)
│   │   ├── models/     # 数据库与数据传输模型
│   │   ├── rag/        # RAG 核心组件 (Loader, Splitter, VectorStore)
│   │   └── services/   # 业务逻辑服务
│   ├── pyproject.toml  # uv 依赖管理配置文件
│   ├── init_db.py      # 数据库初始化脚本
│   └── Dockerfile      # 后端运行镜像
├── docs/               # 项目文档与设计规范
│   └── architecture.md # 架构设计与开发规范详情
├── docker-compose.yml  # 全栈容器编排文件
└── README.md           # 项目说明文档
```

---

## 🚀 快速启动指南 (Docker 开发模式)

由于本地环境配置可能因系统而异（特别是前端原生依赖构建问题），本项目**强烈推荐使用纯 Docker 方式**进行日常开发与调试，真正做到开箱即用。

### 1. 环境准备
- 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- 确保 Docker 服务已启动。

### 2. 一键拉起全栈开发环境

在项目根目录下执行开发专用 Compose 文件：

```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

> **注意：** 该模式下，前端使用了 `Dockerfile.dev` 启动 Vite 热更新（HMR），且通过数据卷（Volumes）将宿主机代码实时映射到了容器内。
> 当您在本地 IDE（如 PyCharm/VSCode）修改代码后，容器内的后端（FastAPI Reload）和前端（Vite HMR）都会**自动热更新**。

### 3. 服务访问与使用
启动完成后，您可以通过以下地址访问：
- **前端问答与后台管理界面**：`http://localhost:5173`
- **后端 Swagger API 接口文档**：`http://localhost:8000/docs`

> 此时您可以在本地随意修改 `frontend/` 和 `backend/` 下的源码，保存后浏览器即可实时看到变化，无需在本地安装任何 `node_modules` 或配置 Python 虚拟环境。

---

## 🚀 生产环境部署 (Docker 生产模式)

当需要将系统打包发布到线上服务器时，请使用默认的 `docker-compose.yml`，该模式会对前端进行 Nginx 静态资源打包构建。

```bash
docker-compose up -d --build
```
启动后前端生产地址为：`http://localhost:3000`

---

## 👥 团队协作规范

1. **分支管理**：基于 `develop` 分支检出 `feature/xxx` 进行功能开发。
2. **依赖管理**：后端**必须**使用 `uv add <package>` 添加依赖，禁止直接使用 `pip`。前端使用 `npm install`。
3. **接口契约**：前后端联调需以 FastAPI 生成的 Swagger 文档为准。
4. **文档阅读**：详细的系统架构与数据组织策略请参考 `docs/architecture.md` 及 `data/数据库文档.md`。
