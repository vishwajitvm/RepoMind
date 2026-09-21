# RepoMind — Configuration Guide

All configuration is managed through server-side environment variables loaded via Pydantic `BaseSettings`. Copy `.env.example` to `.env` to customize settings.

## Environment Variables Reference

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async database connection string for FastAPI |
| `DATABASE_URL_SYNC` | `postgresql://...` | Sync database connection string for Alembic & Worker |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis queue connection string |
| `QDRANT_HOST` | `localhost` | Qdrant host (or `qdrant` inside Docker) |
| `QDRANT_PORT` | `6333` | Qdrant HTTP port |
| `QDRANT_COLLECTION` | `repomind_code_chunks` | Default vector collection name |
| `QDRANT_VECTOR_SIZE`| `384` | Dense vector embedding dimension |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | *None* | GitHub PAT for MCP tools & REST API |
| `GEMINI_API_KEY` | *None* | Google GenAI API key for Gemini 1.5 Flash |
| `GROQ_API_KEY` | *None* | Groq API key for Llama 3.3 70B |
| `NVIDIA_API_KEY` | *None* | NVIDIA NIM API key |
| `OPENROUTER_API_KEY` | *None* | OpenRouter API key |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Local Ollama daemon URL |
| `OLLAMA_MODEL` | `deepseek-r1:1.5b` | Model used for local Ollama inference |
| `EMBEDDING_PROVIDER` | `local` | Primary provider (`local`, `gemini`, `ollama`) |
| `TRACENEST_API_KEY` | *None* | TraceNest observability key |
| `LANGSMITH_API_KEY` | *None* | LangSmith LangGraph tracing key |
