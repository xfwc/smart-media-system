# Research & Technical Decisions: 智能传媒内容分析与推荐系统

**Date**: 2026-05-29

## 1. 热榜数据采集策略

**Decision**: 使用 Python `httpx` + `asyncio` 定时任务（APScheduler），每10分钟从第三方热榜聚合接口（如 tophub.today API）采集数据。

**Rationale**:
- 抖音无官方公开API，第三方聚合源是最可行的数据获取方式
- `httpx` 原生支持 async/await，与 FastAPI 异步模型一致
- APScheduler 集成简单，支持 cron 表达式配置采集频率
- 采集到的原始数据先入 MongoDB（原始快照），清洗后入 MySQL（结构化热榜数据）

**Alternatives Considered**:
- Selenium/Playwright 浏览器自动化 → 资源消耗大，不适合服务器端定时任务
- Scrapy 框架 → 功能过重，本项目只需单一数据源

## 2. NLP 技术选型

**Decision**: 使用 `jieba` 分词 + 自定义规则引擎进行基础NLP处理（关键词提取、分类），情感分析使用 Qwen-2.5 模型。

**Rationale**:
- `jieba` 是中文NLP标准库，轻量高效，适合2周快速集成
- 分类采用关键词匹配 + 规则引擎（8个预定义类别），开发成本低
- 情感分析和风险评级充分利用 Qwen 模型的理解能力
- 避免引入重量级NLP框架（如 transformers）的依赖复杂度

**Alternatives Considered**:
- HanLP → 功能更强但依赖重，2周集成风险高
- 纯 Qwen 处理 → 所有分析走API延迟高，成本大

## 3. 协同过滤推荐算法

**Decision**: 混合推荐策略 — 基于内容的推荐（Item CF）作为主推荐 + 用户协同过滤（User CF）作为冷启动补充 + 热度加权作为兜底。

**Rationale**:
- 物品协同过滤（Item CF）基于热点特征向量（关键词、分类、情感），计算稳定且可解释
- 用户协同过滤（User CF）基于用户偏好相似度，解决新用户冷启动
- 热度加权保证无偏好用户也能看到热门内容
- 使用 `numpy/scipy` 实现余弦相似度矩阵，无需引入专用推荐框架

**Alternatives Considered**:
- Surprise/Implicit 库 → 功能全但学习成本高
- 矩阵分解（SVD）→ 效果好但需要较多用户行为数据积累

## 4. Qwen-2.5 模型集成

**Decision**: 通过 HTTP API 调用 Qwen-2.5-72B-Instruct，使用预定义 Prompt 模板引擎（Jinja2），支持降级方案。

**Rationale**:
- Qwen API 方式无需本地GPU部署，降低运维复杂度
- Jinja2 模板引擎支持变量注入和条件渲染，灵活构建不同场景的 Prompt
- 降级方案：API超时或不可用时，使用预设企划模板填充生成基础企划

**Alternatives Considered**:
- 本地部署 Qwen → 需要GPU资源，2周内不可行
- 文心一言 API → 宪法规定 Qwen，不可替换

## 5. A/B 测试框架

**Decision**: 基于 Redis 的分流策略 — 用户ID Hash 到实验分组，不同分组路由到不同推荐策略。

**Rationale**:
- Redis 读写速度快，支持实时分组查询
- Hash 分流保证同一用户始终在同一分组，消除实验偏差
- 实验结果记录到 MySQL，支持简单的转化率对比

**Alternatives Considered**:
- GrowthBook/FeatureFlags 平台 → 引入额外服务，超出2周范围

## 6. 前端技术栈细化

**Decision**: Vue 3 Composition API + Vite + Element Plus + Pinia + Axios + ECharts。

**Rationale**:
- Composition API 提供更好的逻辑复用和类型推断
- Vite 构建速度远超 Webpack，开发体验好
- Element Plus 组件库完整，满足管理系统 + C端展示需求
- ECharts 用于管理后台数据统计可视化

## 7. 部署与CI/CD

**Decision**: Docker Compose 三环境（dev/test/prod），Nginx 反向代理，GitHub Actions CI/CD。

**Rationale**:
- Docker Compose 单机部署，适配项目规模
- Nginx 统一入口，处理静态文件 + API代理 + HTTPS
- GitHub Actions 免费且与 Git 仓库深度集成
- 三环境分离：dev（热重载）、test（集成测试）、prod（生产配置）

## 8. 数据库分域与表设计

**Decision**: MySQL 5个数据库域（user/hot/recommend/plan/idea），共22张表。

**Rationale**: 按微服务域独立 Schema，降低耦合，未来可按需拆分为独立数据库实例。

22 张表清单见 `data-model.md`。
