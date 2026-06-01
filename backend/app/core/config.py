import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    MYSQL_URL: str = "mysql+asyncmy://root:root123@localhost:3306/smart_media"
    REDIS_URL: str = "redis://localhost:6379/0"
    MONGODB_URL: str = "mongodb://localhost:27017"

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Qwen AI
    QWEN_API_KEY: str = ""
    QWEN_API_URL: str = "https://dashscope.aliyuncs.com/api/v1"
    QWEN_MODEL: str = "qwen2.5-72b-instruct"

    # Crawler
    HOT_CRAWL_INTERVAL_MINUTES: int = 10
    HOT_CRAWL_SOURCE: str = "douyin"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # MongoDB Collections
    MONGO_CRAWL_COLLECTION: str = "crawl_raw_data"
    MONGO_API_LOGS_COLLECTION: str = "api_access_logs"
    MONGO_AI_LOGS_COLLECTION: str = "ai_call_logs"
    MONGO_ARCHIVE_COLLECTION: str = "content_plan_archives"

    # App
    APP_NAME: str = "Smart Media System"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
