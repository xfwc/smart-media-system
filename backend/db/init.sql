-- 智能传媒内容分析与推荐系统 - 数据库初始化
-- 5个Schema: user, hot, recommend, plan, idea

CREATE DATABASE IF NOT EXISTS smart_media CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_media;

-- =============================================
-- Domain: user (用户域)
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(120) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    role ENUM('creator','admin','superadmin') DEFAULT 'creator',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_created (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    nickname VARCHAR(50),
    avatar_url VARCHAR(500),
    bio TEXT,
    platform VARCHAR(50),
    followers_count INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_interests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category VARCHAR(20) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_category (user_id, category),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_behavior_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action_type VARCHAR(30) NOT NULL,
    target_type VARCHAR(30),
    target_id INT,
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_action (user_id, action_type, created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================
-- Domain: hot (热榜域)
-- =============================================
CREATE TABLE IF NOT EXISTS hot_topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    `rank` INT NOT NULL,
    heat_value BIGINT NOT NULL,
    category VARCHAR(20),
    source VARCHAR(50) NOT NULL,
    source_url VARCHAR(500),
    summary TEXT,
    batch_id VARCHAR(36) NOT NULL,
    collected_at DATETIME NOT NULL,
    INDEX idx_batch (batch_id),
    INDEX idx_collected (collected_at, `rank`),
    INDEX idx_category (category),
    INDEX idx_source (source)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS topic_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id INT NOT NULL UNIQUE,
    keywords JSON NOT NULL,
    category VARCHAR(20) NOT NULL,
    sentiment ENUM('positive','negative','neutral') NOT NULL,
    sentiment_score FLOAT NOT NULL,
    risk_level ENUM('low','medium','high') NOT NULL,
    risk_reason VARCHAR(500),
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES hot_topics(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS crawl_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    batch_id VARCHAR(36) UNIQUE,
    status ENUM('running','success','failed') NOT NULL,
    items_count INT DEFAULT 0,
    error_message TEXT,
    started_at DATETIME NOT NULL,
    finished_at DATETIME,
    INDEX idx_status (status, started_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS hot_topic_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id INT NOT NULL,
    title VARCHAR(500) NOT NULL,
    `rank` INT NOT NULL,
    heat_value BIGINT NOT NULL,
    batch_id VARCHAR(36) NOT NULL,
    snapshot_at DATETIME NOT NULL,
    INDEX idx_topic_snapshot (topic_id, snapshot_at),
    FOREIGN KEY (topic_id) REFERENCES hot_topics(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================
-- Domain: recommend (推荐域)
-- =============================================
CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    topic_id INT NOT NULL,
    strategy VARCHAR(20) NOT NULL,
    score FLOAT NOT NULL,
    reason VARCHAR(200) NOT NULL,
    match_tags JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_rec (user_id, created_at),
    INDEX idx_topic_rec (topic_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES hot_topics(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS recommendation_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recommend_id INT NOT NULL UNIQUE,
    user_id INT NOT NULL,
    feedback ENUM('liked','disliked') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recommend_id) REFERENCES recommendations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ab_experiments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    strategy VARCHAR(20) NOT NULL,
    traffic_ratio FLOAT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ab_impressions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    experiment_id INT NOT NULL,
    user_id INT NOT NULL,
    recommend_id INT NOT NULL,
    action ENUM('impression','click','like','dislike') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_exp_user (experiment_id, user_id),
    FOREIGN KEY (experiment_id) REFERENCES ab_experiments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recommend_id) REFERENCES recommendations(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================
-- Domain: plan (企划域)
-- =============================================
CREATE TABLE IF NOT EXISTS plan_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    style_tags JSON NOT NULL,
    prompt_template TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS content_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    topic_id INT NOT NULL,
    template_id INT,
    status ENUM('processing','completed','failed') NOT NULL,
    error_message TEXT,
    generated_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_plan (user_id, created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES hot_topics(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES plan_templates(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS plan_intents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL UNIQUE,
    angle TEXT,
    audience TEXT,
    style VARCHAR(50),
    FOREIGN KEY (plan_id) REFERENCES content_plans(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS plan_outputs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL UNIQUE,
    title_suggestions JSON NOT NULL,
    outline JSON NOT NULL,
    shooting_advice TEXT,
    publish_advice TEXT,
    recommended_tags JSON,
    risk_warning TEXT,
    raw_ai_response TEXT,
    FOREIGN KEY (plan_id) REFERENCES content_plans(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS plan_history_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL,
    version INT NOT NULL,
    plan_output_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_plan_ver (plan_id, version),
    FOREIGN KEY (plan_id) REFERENCES content_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_output_id) REFERENCES plan_outputs(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================
-- Domain: idea (点子域)
-- =============================================
CREATE TABLE IF NOT EXISTS ideas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(20) NOT NULL,
    tags JSON,
    related_topic_id INT,
    is_anonymous BOOLEAN DEFAULT FALSE,
    status ENUM('pending','approved','rejected') DEFAULT 'pending',
    likes_count INT DEFAULT 0,
    comments_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status_time (status, created_at),
    INDEX idx_category_time (category, created_at),
    INDEX idx_user_idea (user_id, created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (related_topic_id) REFERENCES hot_topics(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS idea_likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    idea_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_idea_user (idea_id, user_id),
    FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS idea_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    idea_id INT NOT NULL,
    user_id INT NOT NULL,
    parent_id INT,
    content VARCHAR(500) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_idea_comments (idea_id, created_at),
    FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES idea_comments(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS review_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    idea_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    action ENUM('approve','reject') NOT NULL,
    reason VARCHAR(500),
    reviewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_idea_review (idea_id),
    FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS idea_hot_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    idea_id INT NOT NULL UNIQUE,
    score FLOAT NOT NULL,
    likes_weight FLOAT NOT NULL,
    comments_weight FLOAT NOT NULL,
    time_decay FLOAT NOT NULL,
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE
) ENGINE=InnoDB;
