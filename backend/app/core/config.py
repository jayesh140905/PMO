from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "VigorousONE AI PMO"
    environment: str = "dev"
    database_url: str = "sqlite+pysqlite:///./vigorousone.db"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    token_expiry_minutes: int = 120
    openai_api_key: str | None = None
    ai_model: str = "gpt-4.1-mini"
    enable_mock_ai: bool = True


settings = Settings()
