import os
from typing import List, Optional
from pydantic import Field

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseConfig
    # Fallback class for environments before pydantic-settings installation
    class BaseSettings:
        def __init__(self, **values):
            for k, v in values.items():
                setattr(self, k, v)


class Settings(BaseSettings):
    APP_NAME: str = "FinTech Multi-Agent Platform"
    ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database: Default SQLite for easy zero-setup local runs, MySQL / Postgres in prod
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./fintech_platform.db"
    )

    # LLM & Embedding Engine: "ollama", "mock", or "gemini"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "mock")

    # Local Ollama Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_CHAT_MODEL: str = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2")
    OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

    # Cloud LLM Settings
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)

    # Auth0 & Multi-Tenancy
    MOCK_AUTH_ENABLED: bool = os.getenv("MOCK_AUTH_ENABLED", "True").lower() in ("true", "1", "t")
    AUTH0_DOMAIN: str = os.getenv("AUTH0_DOMAIN", "dev-example.us.auth0.com")
    AUTH0_AUDIENCE: str = os.getenv("AUTH0_AUDIENCE", "https://api.fintech-multi-agent.local")
    AUTH0_ISSUER: str = os.getenv("AUTH0_ISSUER", "https://dev-example.us.auth0.com/")
    AUTH0_ALGORITHMS: List[str] = ["RS256"]

    # File uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
