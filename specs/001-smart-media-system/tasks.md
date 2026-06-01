# Tasks: 智能传媒内容分析与推荐系统

**Input**: Design documents from `specs/001-smart-media-system/`

**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Tests are OPTIONAL for MVP — covered in Polish phase (T060-T061) per constitution minimums (backend ≥80%, frontend ≥70%).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Team Assignment**:
- 🟦 **金帅**(组长): 架构协调 + gateway + admin API
- 🟩 **孙家祺**(后端): user + recommend services, recommendation algorithm
- 🟨 **肇启冰**(NLP/AI): hot + plan services, crawler, NLP, Qwen integration
- 🟥 **董小康**(前端): All frontend pages + components + stores

## Format: `- [ ] [ID] [P?] [Story] Description (Assignee)`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- **(Assignee)**: Recommended team member 🟦🟩🟨🟥

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [x] T001 Create project directory structure per plan.md: `backend/app/{api,models,schemas,services,core,db}`, `frontend/src/{views,components,store,router,api,utils}`, `nginx/`, root `docker-compose.yml` (🟦)
- [x] T002 [P] Initialize frontend project with Vite + Vue 3 + deps in `frontend/package.json` (Element Plus, Pinia, Vue Router, Axios, ECharts) (🟥)
- [x] T003 [P] Initialize backend project with `pyproject.toml` + `requirements.txt` (FastAPI 0.110+, SQLAlchemy 2.0+, Alembic, Pydantic v2, jieba, httpx, passlib[bcrypt], python-jose) (🟩)
- [x] T004 [P] Create `docker-compose.yml` with services: mysql 8.0, redis 7.2, mongodb 7.0, backend, frontend, nginx — three profiles (dev/test/prod) (🟦)
- [x] T005 [P] Configure linting: ESLint + Prettier in `frontend/.eslintrc.cjs` and `frontend/.prettierrc`, Black + mypy in `backend/pyproject.toml` (🟥 🟩 split: T005a frontend 🟥, T005b backend 🟩)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Setup MySQL database: create 5 schemas (`user`, `hot`, `recommend`, `plan`, `idea`) via init SQL in `backend/db/init.sql` (🟦)
- [x] T007 Create Alembic configuration in `backend/alembic/` with `alembic.ini`, `env.py` pointing to all 5 schemas (🟩)
- [x] T008 [P] Create Redis connection manager in `backend/app/db/redis.py` with connection pool, TTL defaults (🟩)
- [x] T009 [P] Create MongoDB connection manager in `backend/app/db/mongodb.py` with 4 collections (`crawl_raw_data`, `api_access_logs`, `ai_call_logs`, `content_plan_archives`) (🟨)
- [x] T010 [P] Create core config module in `backend/app/core/config.py`: environment vars (MYSQL_URL, REDIS_URL, MONGODB_URL, QWEN_API_KEY, JWT_SECRET_KEY), Pydantic Settings, `.env.example` (🟦)
- [x] T011 [P] Create Nginx reverse proxy config in `nginx/default.conf`: static file serving + `/api/v1/` proxy_pass to backend + `/api/docs` pass-through (🟦)
- [x] T012 Create User model in `backend/app/models/user.py`: `users`, `user_profiles`, `user_interests`, `user_behavior_logs` tables + Alembic migration (🟩)
- [x] T013 Create API gateway in `backend/app/api/gateway/`: JWT authentication middleware (`backend/app/core/security.py` with bcrypt + JWT encode/decode), token-bucket rate limiter (`backend/app/core/rate_limit.py`), FastAPI app factory in `backend/app/main.py` (🟦)
- [x] T014 [P] Setup unified error handling and response schemas in `backend/app/schemas/common.py`: standard `ApiResponse[T]`, pagination schema, error response format (🟩)
- [x] T015 [P] Create frontend base layout in `frontend/src/App.vue` + `frontend/src/router/index.js` (route definitions for all 7 pages, auth guard) + `frontend/src/store/index.js` (Pinia init) + `frontend/src/api/request.js` (Axios instance with JWT interceptor) (🟥)
- [x] T016 Setup logging infrastructure: request/response logging middleware → MongoDB `api_access_logs` collection in `backend/app/core/logging.py` (🟨)

**Checkpoint**: Foundation ready — user story implementation can now begin. `docker-compose up` should start all infrastructure services.

---

## Phase 3: User Story 1 — 用户注册、登录与偏好设置 (Priority: P1) 🎯 MVP

**Goal**: 创作者可注册账号、登录系统、设置创作领域偏好

**Independent Test**: 注册新账号 → 登录 → 进入个人中心 → 选择多个创作领域 → 保存，验证JWT认证和偏好持久化

**Assignee**: 🟩 孙家祺 (backend) + 🟥 董小康 (frontend)

### Implementation for User Story 1

- [x] T017 [P] [US1] Create auth schemas in `backend/app/schemas/auth.py`: RegisterRequest, LoginRequest, TokenResponse, UserResponse (🟩)
- [x] T018 [P] [US1] Create user profile/interest schemas in `backend/app/schemas/user.py`: ProfileUpdate, InterestRequest, UserProfileResponse (🟩)
- [x] T019 [US1] Implement auth service in `backend/app/services/user/auth_service.py`: register (bcrypt hash + validation), login (verify + JWT issue), get_current_user (🟩)
- [x] T020 [US1] Implement user service in `backend/app/services/user/user_service.py`: profile CRUD, interest management (add/remove/list) (🟩)
- [x] T021 [US1] Create auth API endpoints in `backend/app/api/user/auth.py`: POST `/auth/register`, POST `/auth/login`, GET `/auth/me` per `contracts/auth-api.yaml` (🟩)
- [x] T022 [US1] Create user profile API endpoints in `backend/app/api/user/profile.py`: GET/PUT `/user/profile`, GET/POST/DELETE `/user/interests` (🟩)
- [x] T023 [P] [US1] Create frontend Login page in `frontend/src/views/Login.vue`: form validation, Axios login call, store token, redirect (🟥)
- [x] T024 [P] [US1] Create frontend Register page in `frontend/src/views/Register.vue`: username/email/phone/password form, validation, auto-login after register (🟥)
- [x] T025 [US1] Create frontend auth store in `frontend/src/store/auth.js`: token storage, login/logout actions, user state, JWT decode for expiry check (🟥)
- [x] T026 [US1] Create frontend Personal Center / Preferences page in `frontend/src/views/Profile.vue`: profile edit, multi-select interest categories, save feedback (🟥)

**Checkpoint**: User can register → login → set interests → view profile. JWT auth works end-to-end.

---

## Phase 4: User Story 2 — 查看热榜与热点分析 (Priority: P1) 🎯 MVP

**Goal**: 创作者可浏览热榜数据，查看每个热点的关键词、分类、情感分析和风险评级

**Independent Test**: 打开热榜页 → 查看排名列表 → 按分类筛选 → 搜索关键词 → 点击热点查看分析详情（关键词/情感/风险）

**Assignee**: 🟨 肇启冰 (backend) + 🟥 董小康 (frontend)

### Implementation for User Story 2

- [x] T027 [US2] Create hot_topic models in `backend/app/models/hot.py`: `hot_topics`, `topic_analysis`, `crawl_tasks`, `hot_topic_history` tables + Alembic migration (🟨)
- [x] T028 [P] [US2] Create hot topic schemas in `backend/app/schemas/hot.py`: HotTopicListResponse, HotTopicDetailResponse, TopicAnalysisResponse with pagination (🟨)
- [x] T029 [US2] Implement crawler service in `backend/app/services/crawler/douyin_crawler.py`: httpx async fetch from tophub.today API, parse response, store raw JSON to MongoDB, batch insert to MySQL (🟨)
- [x] T030 [US2] Implement crawler scheduler in `backend/app/services/crawler/scheduler.py`: APScheduler cron job every 10 minutes, error handling, crawl status tracking in `crawl_tasks` table (🟨)
- [x] T031 [US2] Implement NLP service in `backend/app/services/nlp/analyzer.py`: jieba tokenizer, keyword extraction (TF-IDF), rule-based classification (8 categories), call Qwen for sentiment analysis and risk assessment (🟨)
- [x] T032 [US2] Implement NLP pipeline in `backend/app/services/nlp/pipeline.py`: on new crawl batch → trigger analysis for each new topic → store results in `topic_analysis` table (🟨)
- [x] T033 [US2] Create Redis cache for hot topics in `backend/app/services/crawler/cache.py`: cache hot list with 10min TTL, cache individual analysis results, invalidate on new batch (🟨)
- [x] T034 [US2] Create hot topic API endpoints in `backend/app/api/hot/routes.py`: GET `/hot/list` (paginated + filter + search + sort), GET `/hot/{id}`, GET `/hot/{id}/analysis` per `contracts/hot-api.yaml` (🟨)
- [x] T035 [P] [US2] Create frontend HotList page in `frontend/src/views/HotList.vue`: ranking list with heat indicators, category tabs, sort controls (rank/heat/time), keyword search bar (🟥)
- [x] T036 [US2] Create frontend TopicDetail page in `frontend/src/views/TopicDetail.vue`: full topic info, analysis section (keywords tags, sentiment gauge, risk badge), "生成企划" CTA button (🟥)

**Checkpoint**: Hot list displays with real/simulated data. Analysis results visible per topic. Caching active.

---

## Phase 5: User Story 3 — 获取个性化选题推荐 (Priority: P1) 🎯 MVP

**Goal**: 系统根据用户创作偏好自动推荐匹配的选题，附带推荐分数和理由

**Independent Test**: 设置偏好后访问推荐页 → 验证推荐列表匹配偏好 → 点击喜欢/不喜欢反馈 → 查看推荐历史

**Assignee**: 🟩 孙家祺 (backend) + 🟥 董小康 (frontend)

### Implementation for User Story 3

- [x] T037 [US3] Create recommendation models in `backend/app/models/recommend.py`: `recommendations`, `recommendation_feedback`, `ab_experiments`, `ab_impressions` tables + Alembic migration (🟩)
- [x] T038 [P] [US3] Create recommendation schemas in `backend/app/schemas/recommend.py`: RecommendListResponse, FeedbackRequest, ABStatsResponse (🟩)
- [x] T039 [P] [US3] Implement content-based CF algorithm in `backend/app/services/recommend/content_cf.py`: topic feature vector construction (keywords+category+sentiment), cosine similarity matrix with numpy, score normalization to 0-100 (🟩)
- [x] T040 [P] [US3] Implement user-based CF algorithm in `backend/app/services/recommend/user_cf.py`: user interest similarity, find similar users' liked topics, cold-start fallback to hot items (🟩)
- [x] T041 [US3] Implement recommendation orchestrator in `backend/app/services/recommend/service.py`: strategy selector (content/user/hot/mixed), merge and deduplicate results, generate recommendation reasons from match_tags, persist to `recommendations` table (🟩)
- [x] T042 [US3] Implement A/B test framework in `backend/app/services/recommend/ab_test.py`: Redis-based user hash sharding, experiment group assignment, impression/click tracking (🟩)
- [x] T043 [US3] Create recommendation API in `backend/app/api/recommend/routes.py`: GET `/recommend` (paginated), POST `/recommend/feedback`, GET `/recommend/history`, GET `/recommend/ab-stats` per `contracts/recommend-api.yaml` (🟩)
- [x] T044 [US3] Create frontend Recommend page in `frontend/src/views/Recommend.vue`: personalized feed, score + reason display per item, like/dislike buttons, strategy badge, history tab (🟥)

**Checkpoint**: Recommendation engine works with at least content-based CF. User can see scored recommendations and provide feedback.

---

## Phase 6: User Story 4 — 生成内容企划案 (Priority: P1) 🎯 MVP

**Goal**: 用户选择热点 → 输入创作意图 → AI生成完整企划案（标题/大纲/建议/风险）

**Independent Test**: 从热榜选热点 → 填写创作意图 → 等待生成 → 查看企划（3标题+4步大纲+拍摄建议+风险提示）→ 查看历史企划

**Assignee**: 🟨 肇启冰 (backend) + 🟥 董小康 (frontend)

### Implementation for User Story 4

- [x] T045 [US4] Create content_plan models in `backend/app/models/plan.py`: `content_plans`, `plan_intents`, `plan_outputs`, `plan_templates`, `plan_history_versions` tables + Alembic migration (🟨)
- [x] T046 [P] [US4] Create plan schemas in `backend/app/schemas/plan.py`: PlanGenerateRequest, PlanStatusResponse, PlanDetailResponse, TemplateListResponse (🟨)
- [x] T047 [US4] Create Qwen API client in `backend/app/services/ai/qwen_client.py`: async httpx client with retry + timeout + error handling, parse JSON responses, log to MongoDB `ai_call_logs` (🟨)
- [x] T048 [P] [US4] Create prompt templates in `backend/app/services/ai/prompts/`: `plan_generation.j2` (Jinja2 template with topic info + user intent + style), seed 3 default `plan_templates` rows (知识科普/新闻评论/生活教程) (🟨)
- [x] T049 [US4] Implement plan generation service in `backend/app/services/ai/plan_service.py`: build prompt from template + topic + intent, call Qwen, parse structured response (title_suggestions/outline/advice/risk), create `plan_outputs`, handle versioning, fallback to template fill if AI unavailable (🟨)
- [x] T050 [US4] Create plan API endpoints in `backend/app/api/plan/routes.py`: POST `/plan/generate` (async 202), GET `/plan/{id}/status` (polling), GET `/plan/{id}`, GET `/plan/history`, GET `/plan/templates` per `contracts/plan-api.yaml` (🟨)
- [x] T051 [US4] Create frontend PlanGenerator page in `frontend/src/views/PlanGenerator.vue`: topic selector, intent form (angle/audience/style), template picker, generation progress (polling), result display with collapsible sections, history drawer (🟥)

**Checkpoint**: Full plan generation pipeline works. AI generates structured content; fallback works if Qwen unavailable.

---

## Phase 7: User Stories 5+6 — 点子库社区：浏览/发布/互动/排序 (Priority: P2)

**Goal**: 创作者可在点子库浏览、发布点子，进行点赞/评论互动，按热度排序

**Independent Test**: 进入点子库 → 浏览列表 → 筛选分类 → 发布新点子 → 对他人点子点赞/评论 → 验证热门排序

**Assignee**: 🟩 孙家祺 (backend) + 🟥 董小康 (frontend)

### Implementation for User Stories 5 & 6

- [x] T052 [US5] Create idea models in `backend/app/models/idea.py`: `ideas`, `idea_likes`, `idea_comments`, `idea_hot_scores`, `review_records` tables + Alembic migration (🟩)
- [x] T053 [P] [US5] Create idea schemas in `backend/app/schemas/idea.py`: IdeaListResponse, IdeaDetailResponse, IdeaCreateRequest, CommentRequest, LikeResponse (🟩)
- [x] T054 [US5] Implement idea service in `backend/app/services/idea_service.py`: CRUD with status='pending' default, category filter, keyword search, pagination, anonymous display handling (🟩)
- [x] T055 [US6] Implement idea interaction endpoints in `backend/app/api/idea/routes.py`: POST `/ideas/{id}/like` (toggle), POST `/ideas/{id}/comments` (with parent_id for replies), GET `/ideas` (list), GET `/ideas/{id}` (detail + comments), POST `/ideas` (create) per `contracts/idea-api.yaml` (🟩)
- [x] T056 [US6] Implement hot ranking service in `backend/app/services/ranking/hot_ranking.py`: score = (likes × 2.0 + comments × 3.0) / (hours_since_post + 2)^1.5 (gravity decay), scheduled recalculation via APScheduler, store in `idea_hot_scores` (🟩)
- [x] T057 [P] [US5] Create frontend IdeaHub page in `frontend/src/views/IdeaHub.vue`: card grid/list toggle, category filter tabs, sort selector (hot/new), search bar, "发布点子" FAB button, infinite scroll pagination (🟥)
- [x] T058 [P] [US5] Create frontend IdeaCreate page in `frontend/src/views/IdeaCreate.vue`: title + content editor, category picker, optional topic linkage, anonymous toggle, preview before submit (🟥)
- [x] T059 [US6] Create frontend IdeaDetail page in `frontend/src/views/IdeaDetail.vue`: full content display, like button (animated), comment list with nested replies, comment input, author info (or "匿名用户") (🟥)

**Checkpoint**: Idea hub fully functional. Users can browse, post, like, comment. Hot ranking works.

---

## Phase 8: User Story 7 — 管理员内容审核与统计 (Priority: P3)

**Goal**: 管理员审核用户发布内容，查看运营数据统计

**Independent Test**: 管理员登录 → 查看待审核列表 → 通过/拒绝点子 → 查看统计仪表板

**Assignee**: 🟦 金帅 (backend) + 🟥 董小康 (frontend)

### Implementation for User Story 7

- [x] T060 [US7] Implement admin endpoints in `backend/app/api/admin/routes.py`: GET `/admin/ideas/pending`, POST `/admin/ideas/{id}/review` (approve/reject with reason), GET `/admin/stats` (user/topic/recommend/plan/idea counts + daily trend) per `contracts/idea-api.yaml` admin section (🟦)
- [x] T061 [US7] Create frontend AdminPanel page in `frontend/src/views/AdminPanel.vue`: role-based route guard (admin only), pending review list with approve/reject actions, statistics dashboard with ECharts (user growth line, idea trend bar, recommendation funnel) (🟥)

**Checkpoint**: Admin can review content and view operational metrics.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Quality improvements, deployment readiness, and documentation

- [x] T062 [P] Create seed data script in `backend/scripts/seed_data.py`: insert sample users (admin + 3 creators), 50 mock hot topics with analysis, 10 sample ideas, 5 plan templates (🟨)
- [x] T063 [P] Create `docker-compose.prod.yml` with production config: no hot-reload, gunicorn workers, health checks, resource limits (🟦)
- [x] T064 [P] Create GitHub Actions CI/CD in `.github/workflows/ci.yml`: lint → test (pytest + vitest) → build Docker images → push (🟦)
- [ ] T065 Optimize MySQL indexes: verify indexes on `hot_topics(category, collected_at)`, `recommendations(user_id, created_at)`, `ideas(status, created_at)`, `idea_comments(idea_id, created_at)` per data-model.md (🟩)
- [ ] T066 Verify Redis caching: hot list TTL=10min, analysis cache TTL=1h, session TTL=24h, rate-limit counters in `backend/app/core/rate_limit.py` (🟩)
- [ ] T067 [P] Security audit: verify all passwords use bcrypt, all API endpoints (except register/login/hot list) require JWT, input validation on all POST/PUT, SQL injection check, no secrets in codebase (🟦)
- [ ] T068 [P] Add loading/empty/error states to all frontend pages: skeleton loaders, empty state illustrations, error retry buttons (🟥)
- [ ] T069 Validate quickstart.md: run through `docker-compose up` fresh setup → `seed_data.py` → verify all 7 pages load correctly (🟦)
- [x] T070 [P] Write README.md in project root: project overview, architecture diagram (text-based), tech stack, quickstart link, team info (🟦)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ──────────────────────────────────────────────────────┐
    ↓                                                                 │
Phase 2: Foundational (BLOCKS all user stories)                       │
    ↓                                                                 │
    ├── Phase 3: US1 (用户系统) ──── can start in parallel ──────┐   │
    ├── Phase 4: US2 (热榜分析) ──── with US3, US4 ─────────────┤   │
    ├── Phase 5: US3 (推荐) ─────────────────────────────────────┤   │
    ├── Phase 6: US4 (企划生成) ─────────────────────────────────┤   │
    ├── Phase 7: US5+US6 (点子库) ─── requires US1 complete ─────┤   │
    └── Phase 8: US7 (管理员) ─────── requires US5+US6 complete ─┘   │
                                                                      │
    All stories complete → Phase 9: Polish                            │
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|-----------|-------------------|
| US1 (P1) | Phase 2 only | US2, US3, US4 |
| US2 (P1) | Phase 2 only | US1, US3, US4 |
| US3 (P1) | Phase 2 only (needs US1 user/interests for real data, but can dev with mock) | US1, US2, US4 |
| US4 (P1) | Phase 2 + US2 (needs hot_topics data) | US1, US3 |
| US5+US6 (P2) | Phase 2 + US1 (auth) | — |
| US7 (P3) | Phase 2 + US5+US6 (needs ideas + review_records) | — |

### Within Each User Story

1. Models + Schemas (can parallel) → Services → API Endpoints → Frontend Pages
2. Frontend API layer (`frontend/src/api/`) can be developed in parallel with backend endpoints once contracts are agreed

---

## Parallel Opportunities (4-Person Team)

### Week 1 Parallel Execution

```text
Day 1-2 (All hands on Phase 1+2):
  🟦 T001, T004, T006, T010, T011, T013
  🟩 T003, T005b, T007, T008, T012, T014
  🟨 T003, T005a*, T009, T016  (*frontend lint shared with 🟥)
  🟥 T002, T005a, T015

Day 3-7 (Phase 2 checkpoint reached → Parallel story development):
  🟩 US1: T017-T022 (backend) → passes to 🟥 for T023-T026
  🟨 US2: T027-T034 (backend) → passes to 🟥 for T035-T036
  🟥 US1 frontend T023-T026 + US2 frontend T035-T036
  🟦 floats: code review + gateway tuning + prepare US3 contracts
```

### Week 2 Parallel Execution

```text
Day 8-10:
  🟩 US3: T037-T043 (backend) + T044 passes to 🟥
  🟨 US4: T045-T050 (backend) + T051 passes to 🟥
  🟥 US3 frontend T044 + US4 frontend T051
  🟦 US7 backend prep T060 + Docker prod T063

Day 11-12:
  🟩 US5+US6: T052-T056 (backend)
  🟨 Polish: T062 seed data + Qwen tuning
  🟥 US5+US6 frontend T057-T059 + US7 frontend T061
  🟦 Polish: T064-T067

Day 13-14:
  All: T068-T070 (QA, bug fixes, README, quickstart validation)
```

### Parallel Examples per Story

```bash
# US2: Launch models + schemas together
Task T027: "Create hot_topic models in backend/app/models/hot.py" 🟨
Task T028: "Create hot topic schemas in backend/app/schemas/hot.py" 🟨

# US2: Launch crawler + NLP + cache in parallel (different files)
Task T029: "Implement crawler service in backend/app/services/crawler/douyin_crawler.py" 🟨
Task T031: "Implement NLP service in backend/app/services/nlp/analyzer.py" 🟨
Task T033: "Create Redis cache in backend/app/services/crawler/cache.py" 🟨

# US3: Launch both CF algorithms in parallel
Task T039: "Implement content-based CF in backend/app/services/recommend/content_cf.py" 🟩
Task T040: "Implement user-based CF in backend/app/services/recommend/user_cf.py" 🟩

# US5+US6: Backend + Frontend parallel
Task T054-T056 (idea service + interactions + ranking) 🟩 || Task T057-T058 (IdeaHub + IdeaCreate pages) 🟥
```

---

## Implementation Strategy

### MVP First (User Stories 1-4, P1 Only)

1. Complete Phase 1: Setup (Day 1-2)
2. Complete Phase 2: Foundational (Day 2-3) — **CRITICAL GATE**
3. Complete Phase 3-6: US1 + US2 + US3 + US4 in parallel (Day 3-10)
4. **STOP and VALIDATE**: Test "注册→热榜→推荐→企划生成" full user journey
5. Deploy/demo MVP if ready — this covers the core value proposition

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. US1 + US2 → Hot list with auth (Demo milestone 1)
3. + US3 + US4 → Full recommendation + plan generation (MVP milestone!)
4. + US5+US6 → Idea hub community (Enhanced milestone)
5. + US7 → Admin panel (Complete milestone)
6. Polish → Production ready

### Notes

- **[P] tasks** = different files, no dependencies — can run in parallel
- **[Story]** label maps task to specific user story for traceability
- **(🟦🟩🟨🟥)** = recommended assignee based on team roles
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
