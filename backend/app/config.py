from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://pitchvision:pitchvision_dev_password@localhost:5432/pitchvision_lite"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: str = '["http://localhost:3000"]'
    
    @property
    def cors_origins(self) -> List[str]:
        return json.loads(self.BACKEND_CORS_ORIGINS)
    
    # MinIO / Object Storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_BUCKET: str = "pitchvision-videos"
    MINIO_USE_SSL: bool = False
    
    # CV Pipeline
    CV_MOCK_MODE: bool = True
    CV_MODEL_PATH: str = "/models/yolov8n.pt"
    FFMPEG_PATH: str = "/usr/bin/ffmpeg"
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
