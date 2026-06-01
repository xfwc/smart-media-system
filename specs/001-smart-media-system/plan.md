# Implementation Plan: 智能传媒内容分析与推荐系统

**Branch**: `001-smart-media-system` | **Date**: 2026-05-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-smart-media-system/spec.md`

## Summary

构建面向短视频创作者的智能内容分析与推荐Web平台。核心能力包括：抖音热榜定时采集与分析（NLP）、基于协同过滤的个性化选题推荐、基于Qwen-2.5大模型的AI内容企划自动生成、以及创作者点子库社区。采用前后端分离微服务架构，6个服务按业务域拆分，MySQL+Redis+MongoDB多数据源。4人团队2周交付MVP。

## Technical Context

**Language/Version**: Python 3.11 (backend), JavaScript ES2022 / Vue 3.4+ (frontend)

**Primary Dependencies**:
- Backend: FastAPI 0.110+, SQLAlchemy 2.0+, Alembic (migrations), Pydantic v2, jieba (分词), httpx (async HTTP), passlib[bcrypt], python-jose (JWT)
- Frontend: Vue 3, Vite, Element Plus, Pinia 2.0+, Vue Router 4, Axios, ECharts
- AI: Qwen-2.5-72B-Instruct (via API)
- Infra: Docker Compose, Nginx, GitHub Actions

**Storage**: MySQL 8.0 (5 domains, 22 tables), Redis 7.2 (cache/session/locks), MongoDB 7.0 (logs/archives)

**Testing**: pytest + pytest-asyncio + httpx (backend), vitest + @vue/test-utils (frontend)

**Target Platform**: Linux server (Docker containers), modern browsers (Chrome/Firefox/Edge latest 2 versions)

**Project Type**: web-service (SPA frontend + microservice backend)

**Performance Goals**: Non-AI API P95 < 500ms, AI generation P95 < 30s, frontend FCP < 1.5s, TTI < 2s, 100 concurrent users

**Constraints**: 2-week sprint (2026-05-28 ~ 2026-06-10), 4-person team, 6 microservices, strict tech stack

**Scale/Scope**: 7 user stories, 28 functional requirements, 9 key entities, ~6 frontend pages, ~40 API endpoints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Verification |
|-----------|--------|-------------|
| I. 前后端分离与微服务 | ✅ PASS | Vue 3 SPA + FastAPI 6 services (gateway/user/hot/recommend/plan/idea), RESTful API v1 |
| II. 多数据源架构 | ✅ PASS | MySQL 8.0 (22 tables) + Redis 7.2 (cache/session) + MongoDB 7.0 (logs), Repository Pattern |
| III. 代码质量与测试 | ✅ PASS | pytest ≥80% backend, vitest ≥70% frontend, PEP 8 + Black, ESLint + Prettier, Conventional Commits |
| IV. 性能标准 | ✅ PASS | Redis cache ≤10min, index optimization, token-bucket rate limiting at gateway |
| V. 安全与合规 | ✅ PASS | JWT ≤24h, BCrypt, env vars for secrets, SQL injection prevention, input validation |
| 技术栈约束 | ✅ PASS | All tech choices match constitution: Vue3, FastAPI, MySQL, Redis, MongoDB, Qwen, Docker |
| 开发流程 | ✅ PASS | 2-week cycle, Git Flow, 4-person team with defined roles |

**GATE RESULT: ALL PASS — No violations. Proceed to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/001-smart-media-system/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
│   ├── auth-api.yaml
│   ├── hot-api.yaml
│   ├── recommend-api.yaml
│   ├── plan-api.yaml
│   └── idea-api.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/                    # API路由层
│   │   ├── gateway/            # API网关 + 限流 + 鉴权中间件
│   │   ├── user/               # 用户注册/登录/资料
│   │   ├── hot/                # 热榜采集/查询/分析
│   │   ├── recommend/          # 推荐算法/AB测试
│   │   ├── plan/               # 企划生成/模板管理
│   │   └── idea/               # 点子CRUD/互动/审核
│   ├── models/                 # SQLAlchemy ORM 模型 (22 tables)
│   ├── schemas/                # Pydantic v2 请求/响应模型
│   ├── services/               # 业务逻辑层
│   │   ├── crawler/            # 热榜数据采集
│   │   ├── nlp/                # 分词/分类/情感/风险分析
│   │   ├── recommend/          # 协同过滤算法
│   │   ├── ai/                 # Qwen API 调用 + Prompt模板
│   │   └── ranking/            # 热门排序算法
│   ├── core/                   # 配置/安全/依赖注入
│   └── db/                     # 数据库连接/会话管理
├── alembic/                    # 数据库迁移脚本
├── tests/
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   └── contract/               # API契约测试
├── Dockerfile
├── requirements.txt
└── pyproject.toml

frontend/
├── src/
│   ├── views/                  # 页面组件 (6 pages)
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   ├── HotList.vue
│   │   ├── Recommend.vue
│   │   ├── PlanGenerator.vue
│   │   ├── IdeaHub.vue
│   │   └── AdminPanel.vue
│   ├── components/             # 公共组件
│   ├── store/                  # Pinia stores
│   ├── router/                 # Vue Router 配置
│   ├── api/                    # Axios API 封装
│   └── utils/                  # 工具函数
├── tests/
│   ├── unit/
│   └── e2e/
├── index.html
├── vite.config.js
└── package.json

docker-compose.yml              # 开发/测试/生产三环境
nginx/
└── default.conf                # Nginx 反向代理配置
```

**Structure Decision**: Web application (Option 2) with `backend/` + `frontend/` at repository root. Backend microservices share a single `app/` directory with domain-based subpackages under `api/` and `services/`. Frontend is a standard Vue 3 SPA structure.

## Complexity Tracking

> No violations to justify. All constitution checks passed.
