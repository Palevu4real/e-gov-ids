from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "E-Gov IDS"
    APP_ENV: str = "development"
    DATABASE_URL: str
    REDIS_URL: str
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Kafka settings (were missing)
    KAFKA_BOOTSTRAP_SERVERS: str = "redpanda:9092"
    KAFKA_TOPIC_DETECTIONS: str = "ids.detections"
    KAFKA_TOPIC_DLQ: str = "ids.dlq"
    
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()