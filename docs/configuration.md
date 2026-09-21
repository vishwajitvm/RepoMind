# RepoMind — Configuration Guide

RepoMind enforces **strict separation of concerns** between the Frontend Single-Page Application and the Backend API / Worker system. The frontend and backend maintain completely independent configuration lifecycles to support independent hosting environments (such as `app.example.com` and `api.example.com`).

---

## 1. Directory Structure

```text
RepoMind/
├── backend/
│   ├── .env                 # Private backend configuration & secrets (GITIGNORED)
│   ├── .env.example         # Template for backend settings
│   └── ...
├── frontend/
│   ├── .env                 # Browser-safe frontend configuration (GITIGNORED)
│   ├── .env.example         # Template for frontend settings
│   └── ...
├── docker-compose.yml       # Production-style multi-container orchestrator
└── .gitignore               # Strict exclusion of all .env files
```

---

## 2. Frontend Configuration (`frontend/.env`)

The React frontend only consumes public, browser-safe environment variables prefixed with `VITE_`.

> **Security Rule**: The frontend must NEVER have access to backend secrets, database passwords, or provider API keys. Never put secret keys in `frontend/.env`.

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Target URL for the RepoMind FastAPI backend. When deployed behind a unified reverse proxy, this can be left empty to use relative `/api` paths. |
| `STORYBOOK_PORT` | `6006` | Host port mapped to the Storybook container development server (`repomind-storybook`). |

Template: `frontend/.env.example`

---

## 3. Backend Configuration (`backend/.env`)

All private application settings, database credentials, vector database endpoints, and LLM API keys live exclusively in `backend/.env` and are loaded via Pydantic `BaseSettings`.

### Server & CORS
| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Runtime environment (`development`, `production`, `test`) |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `SECRET_KEY` | `repomind-secret...` | Cryptographic secret for signing and sessions |
| `HOST` | `0.0.0.0` | Bind host address |
| `PORT` | `8000` | Bind port number |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated list of allowed origins for FastAPI `CORSMiddleware` |

### Databases & Infrastructure
| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async PostgreSQL connection string for FastAPI |
| `DATABASE_URL_SYNC` | `postgresql://...` | Sync PostgreSQL connection string for background workers |
| `POSTGRES_USER` | `postgres` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `POSTGRES_DB` | `repomind` | Database name |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis queue and pub/sub broker URL |
| `QDRANT_HOST` | `localhost` | Qdrant vector database hostname |
| `QDRANT_PORT` | `6333` | Qdrant vector database HTTP port |
| `QDRANT_COLLECTION` | `repomind_code_chunks` | Qdrant collection name for source code chunks |
| `QDRANT_VECTOR_SIZE` | `384` | Dense vector embedding dimension |

### GitHub & MCP Integration
| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | *None* | GitHub Personal Access Token for GitHub MCP server & API |
| `GITHUB_MCP_SERVER_COMMAND` | *None* | Command to launch official GitHub MCP server |

### LLM Providers & Cascade Hierarchy
RepoMind routes all LLM queries through `LLMRouter`, with automatic failover across configured providers:

1. **Google Gemini**: `GEMINI_API_KEY`, `GEMINI_MODEL` (`gemini-1.5-flash`)
2. **Groq**: `GROQ_API_KEY`, `GROQ_MODEL` (`llama-3.3-70b-versatile`)
3. **OpenAI**: `OPENAI_API_KEY`, `OPENAI_MODEL` (`gpt-4o-mini`)
4. **Mistral**: `MISTRAL_API_KEY`, `MISTRAL_MODEL` (`mistral-small-latest`)
5. **DeepSeek (WaveSpeed)**: `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL` (`https://api.wavespeed.ai/v1`), `DEEPSEEK_MODEL` (`deepseek-chat`)
6. **Kimi (Moonshot)**: `KIMI_API_KEY`, `KIMI_BASE_URL` (`https://api.moonshot.cn/v1`), `KIMI_MODEL` (`moonshot-v1-8k`)
7. **NVIDIA NIM**: `NVIDIA_API_KEY`, `NVIDIA_MODEL` (`meta/llama-3.3-70b-instruct`)
8. **OpenRouter**: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` (`meta-llama/llama-3.3-70b-instruct:free`)
9. **Ollama (Local LLM Daemon)**: `OLLAMA_BASE_URL` (`http://localhost:11434`), `OLLAMA_MODEL` (`deepseek-r1:1.5b`)
10. **Local Grounding Adapter**: Deterministic local fallback strictly referencing retrieved codebase context.

### Embedding Providers
Managed via `EmbeddingRouter`:
- `EMBEDDING_PROVIDER`: `local` (default), `gemini`, `openai`, `ollama`
- `GEMINI_EMBEDDING_MODEL`: `text-embedding-004`
- `OPENAI_EMBEDDING_MODEL`: `text-embedding-3-small` (dimension 384)
- `OLLAMA_EMBEDDING_MODEL`: `nomic-embed-text`
- `local`: Deterministic L2-normalized 384-dimensional dense n-gram embeddings (runs anywhere with zero network requirements).

### Observability
- `LANGSMITH_API_KEY`: LangSmith API key for tracing LangGraph executions
- `LANGSMITH_PROJECT`: Project name (default: `repomind`)
- `LANGSMITH_ENDPOINT`: LangSmith tracing endpoint
- `LANGCHAIN_TRACING_V2`: Enable LangSmith tracing (`true` / `false`)
- `TRACENEST_API_KEY`: TraceNest application telemetry key
