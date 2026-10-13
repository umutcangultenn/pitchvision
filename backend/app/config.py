from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://pitchvision:pitchvision_dev_password@localhost:5432/pitchvision_lite"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security — NEVER commit a real secret here; set SECRET_KEY in .env
    SECRET_KEY: str = "dev-secret-change-me-in-production"
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
    CV_MOCK_MODE: bool = False  # Set to False to use real YOLO detection
    CV_MODEL_PATH: str = "/models/yolov8n.pt"
    FFMPEG_PATH: str = "/usr/bin/ffmpeg"

    # File Upload
    UPLOAD_DIR: str = "./uploads"

    # NVIDIA NIM API — load from .env, never hardcode here
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_API_KEY: str = ""  # Set in .env: NVIDIA_API_KEY=nvapi-...
    NVIDIA_MODEL: str = "z-ai/glm-5.1"
    NVIDIA_TIMEOUT: int = 120  # seconds

    # Engine — Field dimensions
    FIELD_TYPE: str = "hali_saha"  # "hali_saha" or "full_pitch"
    HALI_SAHA_LENGTH: float = 50.0  # meters
    HALI_SAHA_WIDTH: float = 30.0  # meters
    FULL_PITCH_LENGTH: float = 105.0
    FULL_PITCH_WIDTH: float = 68.0
    SEGMENT_DURATION_MINUTES: int = 15  # default segment size

    # Engine — Detection thresholds
    MOMENT_DETECTION_CONFIDENCE_THRESHOLD: float = 0.4
    COMPARISON_TIME_WINDOW_SECONDS: float = 10.0

    # AI Safety Rules
    AI_DISCLAIMER: str = (
        "Bu analiz otomatik olarak üretilmiştir ve kesin doğruluk iddiası taşımaz. "
        "Nihai değerlendirme analist gözlemiyle birlikte yapılmalıdır."
    )
    AI_MAX_CONFIDENCE_CLAIM: float = 0.85  # Engine NEVER claims higher

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
