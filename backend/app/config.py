import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "repomind-secret-key-change-in-production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/repomind"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/repomind"
    POSTGRES_DB: str = "repomind"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = "repomind_code_chunks"
    QDRANT_VECTOR_SIZE: int = 384  # Standard dense embedding dimension

    # GitHub
    GITHUB_PERSONAL_ACCESS_TOKEN: Optional[str] = None
    GITHUB_MCP_SERVER_COMMAND: Optional[str] = None

    # LLM Providers
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    NVIDIA_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "deepseek-r1:1.5b"

    # Embedding Providers
    EMBEDDING_PROVIDER: str = "local"  # local, gemini, ollama
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    # Observability
    TRACENEST_API_KEY: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "repomind"
    LANGCHAIN_TRACING_V2: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
