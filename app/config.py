from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+aiomysql://gift:123456@172.21.236.93:3306/ocr"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "wss_metal_gauge"
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_DECODE_RESPONSES: bool = True
    
    SECRET_KEY: str = "ocr-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    OSS_STORAGE_PATH: str = "./storage/images"
    OSS_BASE_URL: str = "http://localhost:8000/api/v1/files"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "../logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
