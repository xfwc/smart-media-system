<!-- SPECKIT START -->
## 项目宪法

所有开发活动 MUST 以 `.specify/memory/constitution.md` 为最高指导文件。

## 当前计划

**Feature**: 智能传媒内容分析与推荐系统
**Plan**: `specs/001-smart-media-system/plan.md`
**Spec**: `specs/001-smart-media-system/spec.md`

## 技术上下文

- **架构**: Vue 3 SPA + FastAPI 6微服务 (gateway/user/hot/recommend/plan/idea)
- **前端**: Vue 3.4+ / Vite / Element Plus / Pinia 2.0+ / Vue Router / Axios
- **后端**: Python 3.11 / FastAPI 0.110+ / SQLAlchemy 2.0+ / Pydantic v2 / Alembic
- **数据库**: MySQL 8.0 (22表) / Redis 7.2 (缓存/会话) / MongoDB 7.0 (日志)
- **AI**: 通义千问 Qwen 2.5-72B-Instruct
- **部署**: Docker Compose + Nginx + GitHub Actions
- **周期**: 2026-05-28 ~ 2026-06-10 (2周)
- **团队**: 金帅(组长) / 孙家祺(后端/算法) / 肇启冰(NLP) / 董小康(前端/测试)
<!-- SPECKIT END -->
