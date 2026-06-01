# Data Model: 智能传媒内容分析与推荐系统

## Overview

5 个数据库域（Schema），22 张表。MySQL 8.0 + SQLAlchemy 2.0 ORM。

## Domain 1: user（用户域）— 4 tables

### users
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | BCrypt密码哈希 |
| email | VARCHAR(120) | UNIQUE, NULLABLE | 邮箱 |
| phone | VARCHAR(20) | UNIQUE, NULLABLE | 手机号 |
| role | ENUM('creator','admin','superadmin') | DEFAULT 'creator' | 角色 |
| is_active | BOOLEAN | DEFAULT TRUE | 激活状态 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE | 更新时间 |

### user_profiles
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| user_id | INT | FK→users.id, UNIQUE | 用户ID |
| nickname | VARCHAR(50) | NULLABLE | 昵称 |
| avatar_url | VARCHAR(500) | NULLABLE | 头像URL |
| bio | TEXT | NULLABLE | 个人简介 |
| platform | VARCHAR(50) | NULLABLE | 主要创作平台 |
| followers_count | INT | DEFAULT 0 | 粉丝数 |

### user_interests
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| user_id | INT | FK→users.id | 用户ID |
| category | VARCHAR(20) | NOT NULL | 兴趣分类 |
| weight | FLOAT | DEFAULT 1.0 | 兴趣权重 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

Index: UNIQUE(user_id, category)

### user_behavior_logs
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| user_id | INT | FK→users.id | 用户ID |
| action_type | VARCHAR(30) | NOT NULL | 行为类型(login/view_topic/view_plan/like_idea/comment) |
| target_type | VARCHAR(30) | NULLABLE | 目标类型 |
| target_id | INT | NULLABLE | 目标ID |
| metadata | JSON | NULLABLE | 扩展数据 |
| created_at | DATETIME | DEFAULT NOW() | 行为时间 |

## Domain 2: hot（热榜域）— 4 tables

### hot_topics
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | 热点ID |
| title | VARCHAR(500) | NOT NULL | 热点标题 |
| rank | INT | NOT NULL | 当前排名 |
| heat_value | BIGINT | NOT NULL | 热度值 |
| category | VARCHAR(20) | NULLABLE | 初始分类 |
| source | VARCHAR(50) | NOT NULL | 数据来源(抖音/微博/头条) |
| source_url | VARCHAR(500) | NULLABLE | 原始链接 |
| summary | TEXT | NULLABLE | 内容摘要 |
| batch_id | VARCHAR(36) | NOT NULL | 采集批次ID |
| collected_at | DATETIME | NOT NULL | 采集时间 |

Index: (collected_at, rank), (category), (batch_id)

### topic_analysis
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| topic_id | INT | FK→hot_topics.id, UNIQUE | 热点ID |
| keywords | JSON | NOT NULL | 关键词列表 ["kw1","kw2"] |
| category | VARCHAR(20) | NOT NULL | NLP分类结果 |
| sentiment | ENUM('positive','negative','neutral') | NOT NULL | 情感倾向 |
| sentiment_score | FLOAT | NOT NULL | 情感分数(-1.0~1.0) |
| risk_level | ENUM('low','medium','high') | NOT NULL | 风险评级 |
| risk_reason | VARCHAR(500) | NULLABLE | 风险原因 |
| analyzed_at | DATETIME | DEFAULT NOW() | 分析时间 |

### crawl_tasks
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| source | VARCHAR(50) | NOT NULL | 采集源 |
| batch_id | VARCHAR(36) | UNIQUE | 批次ID |
| status | ENUM('running','success','failed') | NOT NULL | 状态 |
| items_count | INT | DEFAULT 0 | 采集条数 |
| error_message | TEXT | NULLABLE | 错误信息 |
| started_at | DATETIME | NOT NULL | 开始时间 |
| finished_at | DATETIME | NULLABLE | 结束时间 |

### hot_topic_history
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| topic_id | INT | FK→hot_topics.id | 原热点ID |
| title | VARCHAR(500) | NOT NULL | 快照标题 |
| rank | INT | NOT NULL | 快照排名 |
| heat_value | BIGINT | NOT NULL | 快照热度 |
| batch_id | VARCHAR(36) | NOT NULL | 批次ID |
| snapshot_at | DATETIME | NOT NULL | 快照时间 |

Index: (topic_id, snapshot_at)

## Domain 3: recommend（推荐域）— 4 tables

### recommendations
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| user_id | INT | FK→users.id | 用户ID |
| topic_id | INT | FK→hot_topics.id | 热点ID |
| strategy | VARCHAR(20) | NOT NULL | 推荐策略(content/user/hot/mixed) |
| score | FLOAT | NOT NULL | 推荐分数(0-100) |
| reason | VARCHAR(200) | NOT NULL | 推荐理由 |
| match_tags | JSON | NOT NULL | 匹配标签 |
| created_at | DATETIME | DEFAULT NOW() | 推荐时间 |

Index: (user_id, created_at), (topic_id)

### recommendation_feedback
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| recommend_id | INT | FK→recommendations.id, UNIQUE | 推荐ID |
| user_id | INT | FK→users.id | 用户ID |
| feedback | ENUM('liked','disliked') | NOT NULL | 反馈 |
| created_at | DATETIME | DEFAULT NOW() | 反馈时间 |

### ab_experiments
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| name | VARCHAR(100) | NOT NULL | 实验名称 |
| strategy | VARCHAR(20) | NOT NULL | 推荐策略 |
| traffic_ratio | FLOAT | NOT NULL | 流量比例(0-1) |
| is_active | BOOLEAN | DEFAULT TRUE | 是否启用 |
| started_at | DATETIME | DEFAULT NOW() | 开始时间 |
| ended_at | DATETIME | NULLABLE | 结束时间 |

### ab_impressions
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| experiment_id | INT | FK→ab_experiments.id | 实验ID |
| user_id | INT | FK→users.id | 用户ID |
| recommend_id | INT | FK→recommendations.id | 推荐ID |
| action | ENUM('impression','click','like','dislike') | NOT NULL | 行为 |
| created_at | DATETIME | DEFAULT NOW() | 时间 |

## Domain 4: plan（企划域）— 5 tables

### content_plans
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | 企划ID |
| user_id | INT | FK→users.id | 用户ID |
| topic_id | INT | FK→hot_topics.id | 热点ID |
| template_id | INT | FK→plan_templates.id, NULLABLE | 模板ID |
| status | ENUM('processing','completed','failed') | NOT NULL | 状态 |
| error_message | TEXT | NULLABLE | 失败原因 |
| generated_at | DATETIME | NULLABLE | 生成完成时间 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

### plan_intents
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| plan_id | INT | FK→content_plans.id, UNIQUE | 企划ID |
| angle | TEXT | NULLABLE | 创作角度 |
| audience | TEXT | NULLABLE | 目标受众 |
| style | VARCHAR(50) | NULLABLE | 风格偏好 |

### plan_outputs
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| plan_id | INT | FK→content_plans.id, UNIQUE | 企划ID |
| title_suggestions | JSON | NOT NULL | 标题建议 [{"title":"...","style":"..."}] |
| outline | JSON | NOT NULL | 视频大纲 {"hook":"...","step1":"...","step2":"...","step3":"...","step4":"..."} |
| shooting_advice | TEXT | NULLABLE | 拍摄建议 |
| publish_advice | TEXT | NULLABLE | 发布建议 |
| recommended_tags | JSON | NULLABLE | 推荐标签 |
| risk_warning | TEXT | NULLABLE | 风险提示 |
| raw_ai_response | TEXT | NULLABLE | AI原始响应 |

### plan_templates
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| name | VARCHAR(100) | NOT NULL | 模板名称 |
| description | VARCHAR(500) | NULLABLE | 描述 |
| style_tags | JSON | NOT NULL | 风格标签 |
| prompt_template | TEXT | NOT NULL | Prompt模板(Jinja2) |
| is_active | BOOLEAN | DEFAULT TRUE | 是否启用 |

### plan_history_versions
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| plan_id | INT | FK→content_plans.id | 企划ID |
| version | INT | NOT NULL | 版本号 |
| plan_output_id | INT | FK→plan_outputs.id | 输出ID |
| created_at | DATETIME | DEFAULT NOW() | 版本时间 |

## Domain 5: idea（点子域）— 5 tables

### ideas
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | 点子ID |
| user_id | INT | FK→users.id | 作者ID |
| title | VARCHAR(100) | NOT NULL | 标题 |
| content | TEXT | NOT NULL | 正文 |
| category | VARCHAR(20) | NOT NULL | 分类 |
| tags | JSON | NULLABLE | 标签 |
| related_topic_id | INT | FK→hot_topics.id, NULLABLE | 关联热点 |
| is_anonymous | BOOLEAN | DEFAULT FALSE | 匿名发布 |
| status | ENUM('pending','approved','rejected') | DEFAULT 'pending' | 审核状态 |
| likes_count | INT | DEFAULT 0 | 点赞数(冗余) |
| comments_count | INT | DEFAULT 0 | 评论数(冗余) |
| created_at | DATETIME | DEFAULT NOW() | 发布时间 |
| updated_at | DATETIME | ON UPDATE | 更新时间 |

Index: (status, created_at), (category, created_at)

### idea_likes
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| idea_id | INT | FK→ideas.id | 点子ID |
| user_id | INT | FK→users.id | 用户ID |
| created_at | DATETIME | DEFAULT NOW() | 点赞时间 |

Index: UNIQUE(idea_id, user_id)

### idea_comments
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| idea_id | INT | FK→ideas.id | 点子ID |
| user_id | INT | FK→users.id | 用户ID |
| parent_id | INT | FK→idea_comments.id, NULLABLE | 父评论ID(嵌套回复) |
| content | VARCHAR(500) | NOT NULL | 评论内容 |
| created_at | DATETIME | DEFAULT NOW() | 评论时间 |

Index: (idea_id, created_at)

### review_records
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| idea_id | INT | FK→ideas.id | 点子ID |
| reviewer_id | INT | FK→users.id | 审核人ID |
| action | ENUM('approve','reject') | NOT NULL | 操作 |
| reason | VARCHAR(500) | NULLABLE | 拒绝原因 |
| reviewed_at | DATETIME | DEFAULT NOW() | 审核时间 |

### idea_hot_scores
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PK, AUTO_INCREMENT | ID |
| idea_id | INT | FK→ideas.id, UNIQUE | 点子ID |
| score | FLOAT | NOT NULL | 热度分 |
| likes_weight | FLOAT | NOT NULL | 点赞权重 |
| comments_weight | FLOAT | NOT NULL | 评论权重 |
| time_decay | FLOAT | NOT NULL | 时间衰减因子 |
| calculated_at | DATETIME | DEFAULT NOW() | 计算时间 |

## Entity Relationships

```
users ──1:N── user_profiles
users ──1:N── user_interests
users ──1:N── user_behavior_logs
users ──1:N── recommendations
users ──1:N── content_plans
users ──1:N── ideas
users ──1:N── idea_likes
users ──1:N── idea_comments
users ──1:N── review_records

hot_topics ──1:1── topic_analysis
hot_topics ──1:N── hot_topic_history
hot_topics ──1:N── recommendations
hot_topics ──1:N── content_plans
hot_topics ──1:N── ideas

recommendations ──1:1── recommendation_feedback
recommendations ──1:N── ab_impressions

content_plans ──1:1── plan_intents
content_plans ──1:1── plan_outputs
content_plans ──1:N── plan_history_versions
content_plans ──N:1── plan_templates

ideas ──1:N── idea_likes
ideas ──1:N── idea_comments
ideas ──1:N── review_records
ideas ──1:1── idea_hot_scores

ab_experiments ──1:N── ab_impressions
```

## MongoDB Collections

| Collection | Purpose | Key Fields |
|-----------|---------|------------|
| `crawl_raw_data` | 热榜原始采集快照 | batch_id, source, raw_json, crawled_at |
| `api_access_logs` | API访问日志 | user_id, method, path, status_code, duration_ms, ip, timestamp |
| `ai_call_logs` | AI模型调用记录 | plan_id, model, prompt_tokens, completion_tokens, duration_ms, success, error |
| `content_plan_archives` | 企划案历史归档 | plan_id, full_output_json, archived_at |
