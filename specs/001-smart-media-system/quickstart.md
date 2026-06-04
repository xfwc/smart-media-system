# Quickstart Guide: 智能传媒内容分析与推荐系统

## 前置要求

- Docker & Docker Compose (24.0+)
- Node.js 18+ / npm 9+
- Python 3.11+ / uv (Python 包管理)
- Git

## 快速启动（Docker Compose）

```bash
# 1. 克隆项目
git clone <repo-url> smart-media-system
cd smart-media-system

# 2. 复制环境变量配置
cp .env.example .env
# 编辑 .env 填入 QWEN_API_KEY 等必要配置

# 3. 启动全部服务 (MySQL + Redis + MongoDB + Backend + Frontend + Nginx)
docker-compose up -d

# 4. 初始化数据库
docker-compose exec backend alembic upgrade head

# 5. 导入初始热榜数据（模拟数据）
docker-compose exec backend python scripts/seed_data.py

# 6. 访问系统
# 前端: http://localhost:8080
# API文档: http://localhost:8080/api/docs
```

## 开发环境（本地运行）

### 后端

```bash
cd backend

# 安装依赖
uv sync

# 启动 MySQL / Redis / MongoDB（仅基础设施）
docker-compose up -d mysql redis mongodb

# 数据库迁移
uv run alembic upgrade head

# 导入模拟数据
uv run python scripts/seed_data.py

# 启动开发服务器（热重载）
uv run uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
# 访问 http://localhost:5173
```

## 运行测试

```bash
# 后端测试
cd backend
uv run pytest tests/ -v --cov=app --cov-report=html

# 前端测试
cd frontend
npm run test
```

## 目录结构概览

```
backend/app/
├── api/          # 6个微服务API路由
├── models/       # 22个ORM模型
├── schemas/      # Pydantic请求/响应模型
├── services/     # 业务逻辑（采集/NLP/推荐/AI/排序）
├── core/         # 配置/安全/中间件
└── db/           # 数据库连接管理

frontend/src/
├── views/        # 7个页面组件
├── components/   # 公共组件
├── store/        # Pinia状态管理
├── router/       # 路由配置
├── api/          # API请求封装
└── utils/        # 工具函数
```

## 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MYSQL_URL` | MySQL连接串 | `mysql://root:password@localhost:3306/smart_media` |
| `REDIS_URL` | Redis连接串 | `redis://localhost:6379/0` |
| `MONGODB_URL` | MongoDB连接串 | `mongodb://localhost:27017` |
| `QWEN_API_KEY` | Qwen API密钥 | (必需) |
| `QWEN_API_URL` | Qwen API地址 | `https://dashscope.aliyuncs.com/api/v1` |
| `JWT_SECRET_KEY` | JWT签名密钥 | (必需，生产环境修改) |
| `HOT_CRAWL_INTERVAL` | 热榜采集间隔(分钟) | `10` |
