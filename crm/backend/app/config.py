from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Multifamily Leads CRM"
    database_url: str = "sqlite+aiosqlite:///./crm.db"
    secret_key: str = "change-me-in-production-use-a-real-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    class Config:
        env_file = ".env"


settings = Settings()
