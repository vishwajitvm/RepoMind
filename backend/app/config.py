import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_file = os.path.join(_backend_dir, ".env")


class Settings(BaseSettings):
    # Environment & Server
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "repomind-secret-key-change-in-production"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS configuration (comma-separated origins)
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # PostgreSQL Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/repomind"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/repomind"
    POSTGRES_DB: str = "repomind"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Qdrant Vector DB
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = "repomind_code_chunks"
    QDRANT_VECTOR_SIZE: int = 384  # Standard dense embedding dimension

    # GitHub / MCP
    GITHUB_PERSONAL_ACCESS_TOKEN: Optional[str] = None
    GITHUB_MCP_SERVER_COMMAND: Optional[str] = None

    # LLM Providers
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    NVIDIA_API_KEY: Optional[str] = None
    NVIDIA_MODEL: str = "meta/llama-3.3-70b-instruct"

    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    MISTRAL_API_KEY: Optional[str] = None
    MISTRAL_MODEL: str = "mistral-small-latest"

    HUGGINGFACE_API_KEY: Optional[str] = None
    HUGGINGFACE_MODEL: str = "meta-llama/Meta-Llama-3-8B-Instruct"

    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.wavespeed.ai/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    KIMI_API_KEY: Optional[str] = None
    KIMI_BASE_URL: str = "https://api.moonshot.cn/v1"
    KIMI_MODEL: str = "moonshot-v1-8k"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "deepseek-r1:1.5b"

    # Embedding Providers
    EMBEDDING_PROVIDER: str = "local"  # local, gemini, ollama, openai
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Observability
    TRACENEST_API_KEY: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "repomind"
    LANGSMITH_ENDPOINT: Optional[str] = None
    LANGCHAIN_TRACING_V2: bool = False

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
