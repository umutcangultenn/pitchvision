from functools import lru_cache
from typing import List

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_KEY = "dev-secret-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = Field(default="PitchVision Lite API", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    secret_key: str = Field(default=_INSECURE_KEY, alias="SECRET_KEY")

    # JWT
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    database_url: str = Field(
        default="postgresql+psycopg2://pitchvision:pitchvision@localhost:5432/pitchvision",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # BACKEND_CORS_ORIGINS (yeni) veya CORS_ORIGINS (eski) — ikisini de kabul et
    cors_origins: str = Field(
        default="",
        validation_alias=AliasChoices("BACKEND_CORS_ORIGINS", "CORS_ORIGINS"),
    )

    # Storage
    storage_backend: str = Field(default="local", alias="STORAGE_BACKEND")
    minio_endpoint: str = Field(default="minio:9000", alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field(default="pitchvision", alias="MINIO_BUCKET")
    minio_use_ssl: bool = Field(default=False, alias="MINIO_USE_SSL")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def strip_cors(cls, v: str | List[str]) -> str:
        if isinstance(v, list):
            return ",".join(v)
        return (v or "").strip()

    def cors_origin_list(self) -> List[str]:
        raw = self.cors_origins.strip()
        if not raw or raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    def validate_secret_key(self) -> None:
        """Call on startup. Rejects insecure default key in production."""
        if not self.debug and self.secret_key == _INSECURE_KEY:
            raise RuntimeError(
                "SECRET_KEY is set to the insecure default value. "
                "Set a strong random SECRET_KEY in production (DEBUG=false)."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()

