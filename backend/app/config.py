from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_debug: bool = True
    database_url: str = "postgresql+psycopg://dealdna:dealdna@localhost:5432/dealdna"
    jwt_secret: str = "change-me"
    
    # LLM Settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-20b"
    
    # Hindsight Memory Settings
    hindsight_api_key: str = ""
    hindsight_api_url: str = "https://api.hindsight.vectorize.io"
    hindsight_bank_id: str = "dealdna"
    
    # Frontend & CORS
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
