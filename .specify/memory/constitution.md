<!--
Sync Impact Report
==================
Version Change: [TEMPLATE] → 1.0.0
Ratification Date: 2026-05-29
Last Amended: 2026-05-29

Modified Principles: N/A (initial creation from template)
Added Sections:
  - Core Principles (5): 前后端分离 + 微服务, 多数据源架构, 代码质量与测试,
    性能标准, 安全与合规
  - 技术栈约束 (固定选型，严禁更改)
  - 开发流程与团队协作 (2周周期，4人团队)
  - Governance (修订流程、版本策略、合规审查)

Removed Sections: N/A

Templates Requiring Updates:
  ✅ plan-template.md — Constitution Check 兼容
  ✅ spec-template.md — 需求章节对齐
  ✅ tasks-template.md — Phase 结构与迭代交付兼容
  ⚠  CODEBUDDY.md — 已更新引用宪法
  ⚠  .specify/templates/commands/ — 目录不存在，无需操作

Follow-up TODOs: None
-->

# 智能传媒内容分析与推荐系统 宪法

## Core Principles

### I. 前后端分离与微服务架构

项目 MUST 遵循前后端分离架构：

- **前端**：Vue 3 SPA，通过 RESTful API 与后端通信；使用 Pinia 状态管理、Element Plus
  组件库。
- **后端**：FastAPI 微服务架构，按业务域拆分为 6 个独立服务：
  `gateway`（API 网关）、`user`（用户）、`hot`（热榜）、`recommend`（推荐）、
  `plan`（企划）、`idea`（点子库）。
- 前后端 MUST 通过版本化 API（`/api/v1/`）通信，接口契约明确，可独立部署和测试。
- 禁止前端直连数据库，禁止绕过 API 网关访问后端服务。

**理由**：前后端分离保障各层独立开发、测试和部署；6 个微服务按业务域拆分，
粒度和团队 4 人规模匹配，避免单体耦合。

### II. 多数据源架构

系统 MUST 按数据特性选用合适的存储引擎：

- **MySQL 8.0**（主存储）：结构化业务数据，按 5 个业务域（`user`、`hot`、
  `recommend`、`plan`、`idea`）组织 Schema，共 22 张表。使用 SQLAlchemy 2.0
  ORM 进行数据访问。
- **Redis 7.2**（缓存层）：热榜数据缓存、用户会话、分布式锁。MUST 设置 TTL
  防止内存溢出。
- **MongoDB 7.0**（日志层）：操作日志、AI 企划案原始内容、历史数据存档。
- 各微服务 MUST 通过仓储层（Repository Pattern）隔离数据访问逻辑。

**理由**：结构化事务（MySQL）、高并发缓存（Redis）、非结构化文档（MongoDB）
各有专用引擎，混用单库会造成性能瓶颈和维护灾难。

### III. 代码质量与测试覆盖

所有代码 MUST 满足以下质量标准：

- **测试覆盖率**：后端 ≥ 80%，前端 ≥ 70%。核心业务逻辑（热榜分析、推荐算法、
  企划生成）MUST 达到 90% 以上。
- **代码规范**：
  - Python：PEP 8 + Black 自动格式化 + mypy 类型检查。
  - JavaScript/Vue：Airbnb 风格指南 + ESLint + Prettier。
- **提交规范**：MUST 遵循 Conventional Commits
  （`feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`），
  禁止无意义提交信息。
- **Code Review**：所有代码合并前 MUST 经过至少 1 名其他成员 Review。
- **异步 IO**：后端所有 IO 操作 MUST 使用 async/await，禁止同步阻塞。

**理由**：2 周快速迭代下，自动化测试和规范化提交是防止回归的唯一有效手段。

### IV. 性能标准

系统 MUST 满足以下性能指标：

- **非 AI 接口**：P95 延迟 < 500ms。
- **AI 生成接口**：P95 延迟 < 30s。
- **前端首屏**：First Contentful Paint < 1.5s，Time to Interactive < 2s。
- **热榜缓存**：Redis 缓存热榜数据，刷新周期 ≤ 10 分钟。
- **数据库查询**：高频查询 MUST 建立索引，禁止 N+1 查询。
- **网关限流**：MUST 基于令牌桶实现，防止单用户过载。

**理由**：短视频创作者对实时性敏感，性能瓶颈直接影响用户留存。

### V. 安全与合规

以下行为严格禁止，违反即阻塞合并：

- ❌ 禁止向 Git 提交敏感信息（密码、API 密钥、Token、证书）。MUST 使用环境变量
  或 Secrets 管理。
- ❌ 禁止生产环境使用假数据（Mock Data）。
- ❌ 禁止直接修改 `main` 分支 —— MUST 通过 feature 分支 + Pull Request 合并。

此外 MUST 执行：

- 用户密码使用 BCrypt 加密存储，禁止明文。
- API 请求使用 JWT Token 鉴权，Token 有效期 ≤ 24 小时。
- 用户输入校验和防 SQL 注入处理。
- 敏感数据（手机号、邮箱）展示时脱敏。

**理由**：媒体平台场景下，安全漏洞和敏感信息泄露可能导致严重法律和声誉风险。

## 技术栈约束

以下技术栈为项目强制约束，未经全员讨论和宪法修订不得更改：

| 层次 | 技术选型 | 版本要求 |
|------|----------|----------|
| 前端框架 | Vue 3 | 3.4+ |
| UI 组件库 | Element Plus | 最新稳定版 |
| 状态管理 | Pinia | 2.0+ |
| 后端框架 | Python FastAPI | 0.110+ |
| ORM | SQLAlchemy | 2.0+ |
| 关系数据库 | MySQL | 8.0+ |
| 缓存 | Redis | 7.2+ |
| 文档数据库 | MongoDB | 7.0+ |
| AI 大模型 | 通义千问 Qwen | 2.5+ |
| 部署 | Docker + Nginx | 最新稳定版 |

**理由**：固定技术栈消除选型争论，确保 2 周周期内聚焦业务实现。

## 开发流程与团队协作

- **项目周期**：2026-05-28 ~ 2026-06-10（2 周），在此期间交付可演示系统。
- **分支策略**：`main` 稳定分支，`develop` 开发分支，功能在 `feature/*` 分支开发。
- **团队角色**：
  - 金帅（组长）：架构决策、进度把控、前后端协调
  - 孙家祺：后端核心开发、推荐算法
  - 肇启冰：NLP 模块、内容分析
  - 董小康：前端开发、测试
- **每日站会**：15 分钟同步，识别阻塞项。
- **CI/CD**：PR 自动 lint + 测试，合并后自动构建 Docker 镜像。

## Governance

- 本宪法是项目最高指导文件，所有技术决策和代码审查 MUST 以此为准。
- 修订流程：
  1. 提出修订 Issue，说明变更内容及理由。
  2. 全队 4 人中至少 3 人同意（含组长）。
  3. 更新 `.specify/memory/constitution.md` 并同步相关模板。
  4. 通过 PR 合并，记录版本变更。
- 版本策略：语义化版本（MAJOR.MINOR.PATCH）。
  - MAJOR：原则删除或重新定义、技术栈重大变更。
  - MINOR：新增原则或章节、扩展指导范围。
  - PATCH：措辞修正、格式调整。
- 合规审查：每个 Sprint 回顾 MUST 逐条对照宪法检查执行情况。

**Version**: 1.0.0 | **Ratified**: 2026-05-29 | **Last Amended**: 2026-05-29
