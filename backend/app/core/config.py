from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Lead Management API"
    environment: str = "development"
    database_url: str = "sqlite:///./leads.db"
    frontend_origin: str = "http://localhost:3000"

    jwt_secret: str = "development-only-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120

    admin_email: str = "attorney@example.com"
    admin_password: str = "change-me"

    upload_dir: str = "./uploads"
    max_upload_bytes: int = 5 * 1024 * 1024

    resend_api_key: str = ""
    email_from: str = "Lead Intake <onboarding@resend.dev>"
    attorney_email: str = "attorney@example.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
