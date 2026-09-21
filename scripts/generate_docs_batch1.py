import os
import base64

def make_mermaid_link(mermaid_code: str, alt_text: str = "Architecture Flow Diagram") -> str:
    clean = mermaid_code.strip()
    b64 = base64.b64encode(clean.encode("utf-8")).decode("ascii")
    url = f"https://mermaid.ink/svg/{b64}"
    return f"![{alt_text}]({url})\n\n```mermaid\n{clean}\n```"

def write_doc(rel_path: str, content: str):
    full_path = os.path.join(os.getcwd(), rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated {rel_path} ({len(content)} bytes)")

# -----------------------------------------------------------------------------
# 1. README.md
# -----------------------------------------------------------------------------
readme_diag = """flowchart TD
    User([Developer / Architect]) -->|1. Natural Language Query| UI[React 18 Single-Page App :3000]
    UI -->|2. POST /api/chat| API[FastAPI Backend :8000]
    
    subgraph Core [LangGraph Orchestrator Engine]
        API --> Graph[LangGraph StateGraph]
        Graph -->|3. Query Vector Embeddings| Qdrant[(Qdrant Vector DB :6333)]
        Graph -->|4. Inspect Live Code & Commits| GitHubMCP[Official GitHub MCP Server]
        Graph -->|5. Multi-Provider Fallback| LLMRouter[LLM Router Engine]
    end

    subgraph Providers [10-Tier Failover Chain]
        LLMRouter --> Gemini[1. Google Gemini Flash]
        LLMRouter --> Groq[2. Groq Llama-3.3 70B]
        LLMRouter --> Nvidia[3. NVIDIA NIM Llama-3.3]
        LLMRouter --> OpenRouter[4. OpenRouter Free Tier]
        LLMRouter --> Ollama[5. Ollama Local Daemon :11434]
        LLMRouter --> LocalEngine[6. Local Grounding Engine]
    end

    subgraph Observability [Trace & Telemetry]
        API --> TraceNest[TraceNest UI :8000/tracenest]
        Graph --> LangSmith[LangSmith Tracing]
    end

    LLMRouter -->|6. Grounded Answer| Graph
    Graph -->|7. Verified Response & Exact Line Citations| UI"""

readme_content = f"""# RepoMind — AI Codebase Intelligence Platform

RepoMind is a modern, production-style AI assistant engineered to help software teams inspect, navigate, and deeply understand complex GitHub repositories with speed and cryptographic precision.

---

## 1. What is RepoMind? (In Plain Language)

Think of RepoMind as a dedicated senior engineer who has read every single line of code in your GitHub repository and remembers how everything connects.

Normally, when you ask a generic AI about a codebase, it guesses, hallucinates functions that do not exist, or asks you to copy-paste thousands of lines of code. RepoMind is fundamentally different:
- **It reads your code structurally**: Instead of cutting code in the middle of sentences or brackets, it understands classes, functions, and interfaces.
- **It searches with semantic memory**: It stores mathematical fingerprints (embeddings) of code snippets inside a high-speed vector search engine (Qdrant).
- **It talks directly to GitHub**: When you need to know about the latest commits or pull requests, it queries the official GitHub Model Context Protocol (MCP) server.
- **It never stops working**: If cloud AI services like Gemini, OpenAI, or Groq run out of tokens or experience rate limits, RepoMind automatically switches to backup AI models—including a completely free, local AI running on your machine via Ollama.
- **It provides exact proofs**: Every single answer includes the exact file names and line numbers so you can verify the truth immediately.

---

## 2. End-to-End System Architecture

{make_mermaid_link(readme_diag, "RepoMind End-to-End System Architecture")}

---

## 3. Technical Core Principles

RepoMind follows a **modular monolith** design pattern adhering strictly to engineering standards:
- **Zero Hallucinated Integrations**: Real external APIs, verified official package dependencies, and strict type checking.
- **Code-Aware Chunking**: AST-guided symbol extraction preserving module, class, function, and interface bounds with file path and line span tracking.
- **Resumable Indexing**: Background workers powered by Redis 7 and asynchronous Python tasks with individual file error boundaries.
- **10-Tier LLM Resilience**: Automatic failover across Gemini, Groq, NVIDIA NIM, OpenRouter, Mistral, DeepSeek, Moonshot/Kimi, OpenAI, and local Ollama.
- **TraceNest Telemetry**: Real-time request and AI execution telemetry served via an embedded dashboard at `http://localhost:8000/tracenest`.
- **Storybook Component Workbench**: Containerized Storybook 8 suite at `http://localhost:6006` showcasing 14 core UI components and 56 interactive states.

---

## 4. Docker-First Quickstart

Everything required by RepoMind runs inside Docker containers. Only **Docker** and **Docker Compose** are required on the host system.

### 4.1 Initialize Configuration
```bash
# Clone the repository
git clone https://github.com/your-org/repomind.git
cd repomind

# Initialize independent frontend and backend environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 4.2 Start the Multi-Service Stack
```bash
docker compose up -d --build
```

### 4.3 Service Ports & Addresses
| Service | Local Address | Description |
| :--- | :--- | :--- |
| **Web Frontend** | [http://localhost:3000](http://localhost:3000) | React 18 Single-Page Application |
| **Storybook UI** | [http://localhost:6006](http://localhost:6006) | Component Design System & Stories |
| **Backend API** | [http://localhost:8000/docs](http://localhost:8000/docs) | FastAPI OpenAPI Documentation |
| **TraceNest Dashboard** | [http://localhost:8000/tracenest](http://localhost:8000/tracenest) | Observability & Telemetry UI |
| **Qdrant Vector DB** | [http://localhost:6333/dashboard](http://localhost:6333/dashboard) | Semantic Vector Search UI |
| **Ollama Local LLM** | [http://localhost:11434](http://localhost:11434) | Local Offline LLM Daemon |

---

## 5. Automated Verification & Testing

Verify the end-to-end integrity of all 9 running containers, vector retrieval, and telemetry:

```bash
# Run comprehensive live Docker integration pipeline
python backend/tests/test_live_docker.py

# Run backend unit test suite
pytest backend/tests -v
```

---

## 6. Complete Documentation Index

- [**System Architecture**](docs/architecture.md) — Architectural overview, layer responsibilities, and data flows.
- [**Configuration Guide**](docs/configuration.md) — Independent environment variables and secret hygiene.
- [**Development Workflow**](docs/development.md) — Local development, hot reloading, and toolchains.
- [**REST API Reference**](docs/api.md) — Complete endpoint schemas, parameters, and curl examples.
- [**Deployment Guide**](docs/deployment.md) — Single-node Docker and distributed cloud hosting.
- [**Testing & Quality**](docs/testing.md) — Pytest, Storybook tests, TypeScript strict checks, and CI.
- [**Troubleshooting Guide**](docs/troubleshooting.md) — Solutions for common issues and diagnostics.
- [**Security Architecture**](docs/security.md) — Credential protection, secret scrubbing, and safe indexing.
- [**Observability Guide**](docs/observability.md) — TraceNest dashboard, LangSmith tracing, and telemetry.
- [**Frontend Architecture**](docs/frontend.md) — React 18, TanStack Query, Tailwind CSS, and Zod forms.
- [**Storybook Catalog**](docs/storybook.md) — UI component library, controls, and states.
- [**Data Model & Storage**](docs/data-model.md) — PostgreSQL relational schema and Qdrant vector payloads.
- [**Feature Deep Dives**](docs/feature/):
  - [Code Chunking](docs/feature/code-chunking.md)
  - [Embeddings](docs/feature/embeddings.md)
  - [Execution Tracing](docs/feature/execution-trace.md)
  - [GitHub MCP](docs/feature/github-mcp.md)
  - [LLM Routing](docs/feature/llm-routing.md)
  - [RAG Chat](docs/feature/rag-chat.md)
  - [Repository Indexing](docs/feature/repository-indexing.md)
"""
write_doc("README.md", readme_content)

# -----------------------------------------------------------------------------
# 2. docs/architecture.md
# -----------------------------------------------------------------------------
arch_diag = """flowchart TD
    subgraph PresentationLayer [Presentation Layer]
        ReactApp[React 18 SPA :3000]
        StorybookApp[Storybook Workbench :6006]
    end

    subgraph ServiceLayer [API & Orchestration Layer]
        FastAPIService[FastAPI REST Engine :8000]
        LangGraphOrchestrator[LangGraph StateGraph]
        EmbeddingRouterService[EmbeddingRouter]
        LLMRouterService[LLMRouter Failover Engine]
    end

    subgraph IngestionLayer [Background Ingestion Subsystem]
        RedisBroker[(Redis 7 Task Queue)]
        IngestionWorker[Background Worker Process]
        GitCloner[Shallow Git Cloner]
        ASTParser[AST Code-Aware Chunking Engine]
    end

    subgraph StorageLayer [Persistence & Retrieval Layer]
        PostgresDB[(PostgreSQL 16 Relational DB)]
        QdrantStore[(Qdrant Vector Database :6333)]
    end

    subgraph ExternalLayer [External Tools & Model Providers]
        GitHubMCPServer[Official GitHub MCP Container]
        CloudLLMProviders[Gemini / Groq / NVIDIA / OpenRouter]
        OllamaDaemon[Ollama Local Daemon :11434]
    end

    subgraph TelemetryLayer [Observability & Monitoring]
        TraceNestEngine[TraceNest Middleware & UI :8000/tracenest]
        LangSmithEngine[LangSmith Tracing]
    end

    ReactApp -->|HTTP REST API| FastAPIService
    FastAPIService -->|Enqueue Job| RedisBroker
    RedisBroker -->|Pop Job| IngestionWorker
    IngestionWorker -->|Clone Repo| GitCloner
    GitCloner -->|Source Files| ASTParser
    ASTParser -->|Code Chunks| EmbeddingRouterService
    EmbeddingRouterService -->|Vectors| QdrantStore
    IngestionWorker -->|Job Status & File Tree| PostgresDB

    FastAPIService -->|Execute Chat| LangGraphOrchestrator
    LangGraphOrchestrator -->|Dense Similarity Retrieval| QdrantStore
    LangGraphOrchestrator -->|Live Source Inspection| GitHubMCPServer
    LangGraphOrchestrator -->|Grounded Answer Synthesis| LLMRouterService
    LLMRouterService -->|Remote Inference| CloudLLMProviders
    LLMRouterService -.->|Offline Fallback| OllamaDaemon
    FastAPIService -->|Telemetry Logs| TraceNestEngine
    LangGraphOrchestrator -->|Graph Execution Traces| LangSmithEngine"""

arch_content = f"""# RepoMind — System Architecture Specification

## 1. System Overview (In Plain Language)

RepoMind is built like an automated research library for software engineering projects.

When developers work with modern codebases consisting of hundreds or thousands of files, answering questions like *"How does error handling work in our database layer?"* requires finding and reading many interrelated files. RepoMind solves this in four logical stages:
1. **Cataloging (Ingestion)**: It clones the repository safely, discards binary and build files, and catalogs every source file.
2. **Reading (AST Chunking)**: Rather than slicing files into arbitrary character chunks that break code syntax, it uses the programming language's grammar rules to break the code into logical pieces (functions, classes, interfaces).
3. **Indexing (Vector Database)**: It converts these code snippets into mathematical vectors (embeddings) that capture the meaning of the code, storing them in Qdrant.
4. **Reasoning (LangGraph & Multi-Provider LLM)**: When you ask a question, RepoMind finds the relevant snippets in Qdrant, verifies recent changes directly on GitHub, and asks an AI model to answer. If the primary AI is unavailable, it automatically rolls over to backup models or a local AI.

---

## 2. Multi-Tier Architecture Diagram

{make_mermaid_link(arch_diag, "RepoMind Multi-Tier System Architecture")}

---

## 3. Detailed Component Responsibilities

### 3.1 Presentation Layer
- **React 18 Single-Page Application (Port 3000)**: Built with TypeScript, Vite, and Tailwind CSS. Connects to the backend via TanStack Query for caching and real-time state synchronization.
- **Storybook UI Workbench (Port 6006)**: Independent development environment hosting isolated stories for all 14 reusable components across idle, loading, success, and error states.

### 3.2 Ingestion & Background Processing Subsystem
- **Redis 7 Broker**: Serves as the task queue for long-running indexing operations, isolating web requests from compute-heavy Git cloning and embedding generation.
- **Background Worker**: Python process executing `app.services.worker`. Clones Git repositories using shallow depth (`--depth 1`), filters ignored and sensitive paths, executes AST parsing, batches embedding generation, and records status in PostgreSQL.
- **Per-File Error Boundaries**: Failures during the parsing of one file do not abort the entire job. Unparseable files are recorded with descriptive errors while the remainder of the repository is fully indexed.

### 3.3 Storage Layer
- **PostgreSQL 16**: System of record for all relational data, including repository metadata, file trees, indexing job progression, chat threads, and execution telemetry traces.
- **Qdrant Vector Database**: Stores 384-dimensional dense vectors with cosine similarity metrics and payload metadata (`path`, `language`, `symbol`, `chunk_type`, `start_line`, `end_line`, `repository_id`).

### 3.4 Intelligence & AI Subsystem
- **LangGraph StateGraph**: Orchestrates the multi-stage query lifecycle:
  - Step 1: `qdrant_retrieval` (semantic vector search).
  - Step 2: `mcp_decision` (deterministic keyword and freshness heuristic).
  - Step 3: `mcp_execution` (optional live code query via GitHub MCP).
  - Step 4: `llm_routing_generation` (multi-provider resilient generation).
- **EmbeddingRouter**: Unified embedding manager with local sentence-transformers, Google Gemini, Ollama, and OpenAI fallbacks.
- **LLMRouter**: 10-tier cascading fallback router: Gemini → Groq → NVIDIA → OpenRouter → Mistral → DeepSeek → Kimi → OpenAI → Ollama → LocalGrounding.

### 3.5 Observability Layer
- **TraceNest**: Integrated logging framework providing automatic HTTP telemetry through `TraceNestMiddleware` and structured JSON logs visualized at `/tracenest/`.
- **LangSmith**: Best-effort LangGraph tracing for multi-step agent flows.
"""
write_doc("docs/architecture.md", arch_content)

# -----------------------------------------------------------------------------
# 3. docs/configuration.md
# -----------------------------------------------------------------------------
config_diag = """flowchart LR
    subgraph FrontendConfig [Frontend Isolation :3000]
        FEnv[frontend/.env] -->|Vite Build-Time / Runtime| ViteApp[React Single-Page App]
        style FEnv fill:#d4edda,stroke:#28a745
    end

    subgraph BackendConfig [Backend Isolation :8000]
        BEnv[backend/.env] -->|Pydantic BaseSettings| FastAPIServer[FastAPI Server]
        BEnv -->|Pydantic BaseSettings| IngestWorker[Ingestion Worker]
        style BEnv fill:#f8d7da,stroke:#dc3545
    end

    subgraph ZeroTrust [Security Boundary]
        ViteApp -.->|Public HTTP Requests Only| FastAPIServer
    end"""

config_content = f"""# RepoMind — Configuration & Environment Specification

## 1. Overview (In Plain Language)

RepoMind separates frontend and backend configuration completely.

Why?
- **Security**: The frontend runs in a user's web browser. Anyone can view the frontend's code. If database passwords or private AI keys were placed in the frontend configuration, anyone on the internet could steal them.
- **Independent Hosting**: The frontend can be hosted on platforms like Vercel or Cloudflare, while the backend runs in Docker or on AWS. Each system only knows what it strictly needs to function.

---

## 2. Configuration Isolation Architecture

{make_mermaid_link(config_diag, "Frontend and Backend Configuration Isolation")}

---

## 3. Directory Layout

```text
RepoMind/
├── backend/
│   ├── .env                 # Private backend configuration & API keys (GITIGNORED)
│   ├── .env.example         # Template with placeholder descriptions
│   └── ...
├── frontend/
│   ├── .env                 # Browser-safe public variables (GITIGNORED)
│   ├── .env.example         # Template with placeholder descriptions
│   └── ...
├── docker-compose.yml       # Production-style multi-container orchestrator
└── .gitignore               # Enforces exclusion of all .env files
```

---

## 4. Frontend Variables (`frontend/.env`)

The frontend only consumes public variables starting with `VITE_`.

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Target URL for the RepoMind FastAPI backend. When deployed behind a reverse proxy, this can be left empty for relative `/api` paths. |
| `STORYBOOK_PORT` | `6006` | Port mapped to the Dockerized Storybook container (`repomind-storybook`). |

---

## 5. Backend Variables (`backend/.env`)

All private application settings, database credentials, vector database endpoints, and LLM API keys live exclusively in `backend/.env` and are loaded via Pydantic `BaseSettings`.

### Server & Infrastructure
| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Runtime environment (`development`, `production`, `test`) |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `PORT` | `8000` | Port for FastAPI application |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed origins for web security headers |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async PostgreSQL connection string for API |
| `DATABASE_URL_SYNC` | `postgresql://...` | Sync PostgreSQL connection string for worker |
| `REDIS_URL` | `redis://redis:6379/0` | Redis queue and broker connection string |
| `QDRANT_HOST` | `qdrant` | Hostname of Qdrant vector database container |
| `QDRANT_PORT` | `6333` | Port for Qdrant REST and gRPC operations |

### LLM Providers & Fallback Chain
| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | `""` | Google Gemini API key (Primary tier) |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model name |
| `GROQ_API_KEY` | `""` | Groq high-speed inference API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model name |
| `NVIDIA_API_KEY` | `""` | NVIDIA NIM API key |
| `NVIDIA_MODEL` | `meta/llama-3.3-70b-instruct` | NVIDIA NIM model name |
| `OPENROUTER_API_KEY` | `""` | OpenRouter multi-model gateway API key |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama local inference endpoint (Offline fallback) |
| `OLLAMA_MODEL` | `deepseek-r1:1.5b` | Model installed in local Ollama daemon |

### GitHub MCP Integration
| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | `""` | GitHub token for MCP live code retrieval |
| `GITHUB_MCP_SERVER_COMMAND` | `""` | Command or endpoint for MCP server |
"""
write_doc("docs/configuration.md", config_content)

# -----------------------------------------------------------------------------
# 4. docs/development.md
# -----------------------------------------------------------------------------
dev_diag = """flowchart TD
    Dev([Engineer]) -->|Edits code locally| LocalFiles[Local Repository]
    LocalFiles -->|Volume Mount :3000| FrontendContainer[repomind-frontend :3000 Vite HMR]
    LocalFiles -->|Volume Mount :6006| StorybookContainer[repomind-storybook :6006]
    LocalFiles -->|Volume Mount :8000| BackendContainer[repomind-backend :8000 Uvicorn]
    LocalFiles -->|Volume Mount| WorkerContainer[repomind-worker Ingestion]
    
    Dev -->|Runs test suite| Pytest[pytest backend/tests]
    Dev -->|Runs UI checks| Typecheck[npm run build / type-check]
    Dev -->|Runs live integration| DockerTest[python backend/tests/test_live_docker.py]"""

dev_content = f"""# RepoMind — Development Workflow Guide

## 1. Overview (In Plain Language)

Developing on RepoMind is built to be fast, reliable, and painless. 

You don't need to install PostgreSQL, Redis, Qdrant, or Ollama directly onto your computer. Docker runs all of these services in isolated containers, while volume mounts allow you to edit code in your local editor (like VS Code or Cursor) and see changes immediately without restarting containers.

---

## 2. Developer Inner Loop Diagram

{make_mermaid_link(dev_diag, "Developer Inner Loop and Live Container Synchronization")}

---

## 3. Quickstart for Developers

### 3.1 Initial Environment Setup
```bash
git clone https://github.com/your-org/repomind.git
cd repomind

cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 3.2 Starting the Full Stack
```bash
docker compose up -d --build
```
This boots all 9 containers with live volume mounts:
- Editing files in `frontend/src/` triggers instant Vite Hot Module Replacement (HMR) at `http://localhost:3000`.
- Editing stories in `frontend/src/stories/` reflects instantly in Storybook at `http://localhost:6006`.
- Editing files in `backend/app/` is mounted directly into `repomind-backend` and `repomind-worker`.

---

## 4. Running Tests & Quality Checks

### 4.1 Backend Pytest Suite
```bash
# Inside local Python environment or backend container
pytest backend/tests -v
```

### 4.2 End-to-End Live Docker Pipeline
```bash
# Executes complete repository creation, indexing, Qdrant retrieval, MCP, and chat
python backend/tests/test_live_docker.py
```

### 4.3 Frontend TypeScript & Lint Checks
```bash
cd frontend
npm run build
```

---

## 5. Working with Storybook

RepoMind uses Storybook as a first-class citizen for UI development. Every reusable component must maintain interactive stories covering idle, loading, success, and error states.

- Access Storybook: [http://localhost:6006](http://localhost:6006)
- Test Storybook build:
  ```bash
  cd frontend
  npm run build-storybook
  ```
"""
write_doc("docs/development.md", dev_content)

# -----------------------------------------------------------------------------
# 5. docs/api.md
# -----------------------------------------------------------------------------
api_diag = """sequenceDiagram
    autonumber
    actor Client as Web Frontend / API Client
    participant API as FastAPI (:8000)
    participant Redis as Redis Queue
    participant Worker as Background Worker
    participant Qdrant as Qdrant Vector DB
    participant LLM as LLM Router

    Client->>API: POST /api/repositories {url: "..."}
    API-->>Client: 201 Created {id, name, status: "pending"}

    Client->>API: POST /api/repositories/{id}/index
    API->>Redis: Enqueue indexing job
    API-->>Client: 202 Accepted {job_id, status: "pending"}

    Worker->>Redis: Dequeue job
    Worker->>Qdrant: Store code chunk vectors
    Worker-->>API: Update job status (completed)

    Client->>API: GET /api/repositories/{id}/status
    API-->>Client: 200 OK {status: "completed", files_indexed: 42}

    Client->>API: POST /api/chat {repository_id, query}
    API->>Qdrant: Similarity search (top-k chunks)
    API->>LLM: Multi-provider synthesis
    API-->>Client: 200 OK {answer, citations, execution_id}"""

api_content = f"""# RepoMind — REST API Specification

## 1. Overview (In Plain Language)

The RepoMind API allows any website, script, or mobile app to communicate with RepoMind. 

It provides standard web endpoints (URLs) to:
1. Register a GitHub repository.
2. Trigger the automated indexing of that repository.
3. Check the progress of the indexing job.
4. Send questions and receive detailed, grounded answers with code citations.
5. Inspect execution traces to see which AI models and search tools were used.

---

## 2. API Request-Response Lifecycle

{make_mermaid_link(api_diag, "API Request-Response Lifecycle and Interactions")}

---

## 3. Endpoints Reference

### 3.1 Health & Telemetry

#### `GET /health`
Returns the operational health of the FastAPI service and environment mode.
- **Response `200 OK`**:
  ```json
  {{
    "status": "healthy",
    "service": "RepoMind API",
    "environment": "development"
  }}
  ```

#### `GET /tracenest` & `GET /tracenest/`
Renders the interactive TraceNest telemetry dashboard displaying real-time execution logs, request latencies, and tool calls.

---

### 3.2 Repositories

#### `POST /api/repositories`
Registers a new GitHub repository for analysis.
- **Request Body**:
  ```json
  {{
    "url": "https://github.com/octocat/Hello-World",
    "branch": "master"
  }}
  ```
- **Response `201 Created`**:
  ```json
  {{
    "id": "cbee282e-bad2-4603-b556-9256fddf1b2f",
    "name": "octocat/Hello-World",
    "url": "https://github.com/octocat/Hello-World",
    "branch": "master",
    "status": "pending",
    "created_at": "2026-09-21T18:00:00Z"
  }}
  ```

#### `GET /api/repositories`
Lists all registered repositories.

#### `POST /api/repositories/{{id}}/index`
Triggers an asynchronous background indexing job for the specified repository.
- **Response `202 Accepted`**:
  ```json
  {{
    "job_id": "8f8b3c10-5231-4ec1-a987-a2f019bca452",
    "repository_id": "cbee282e-bad2-4603-b556-9256fddf1b2f",
    "status": "pending"
  }}
  ```

#### `GET /api/repositories/{{id}}/status`
Returns real-time progress of the indexing job.
- **Response `200 OK`**:
  ```json
  {{
    "repository_id": "cbee282e-bad2-4603-b556-9256fddf1b2f",
    "status": "completed",
    "files_indexed": 12,
    "chunks_created": 48,
    "error": null
  }}
  ```

---

### 3.3 Intelligence & Chat

#### `POST /api/chat`
Submits a natural language query against an indexed repository.
- **Request Body**:
  ```json
  {{
    "repository_id": "cbee282e-bad2-4603-b556-9256fddf1b2f",
    "query": "How is the greeting printed and where is it located?"
  }}
  ```
- **Response `200 OK`**:
  ```json
  {{
    "message_id": "6fee9339-66f7-46b3-8eb4-6bf21a041477",
    "answer": "The greeting is stored in README and printed via standard output...",
    "citations": [
      {{
        "file_path": "README",
        "symbol": "README",
        "start_line": 1,
        "end_line": 2,
        "source_type": "indexed"
      }}
    ],
    "execution_id": "4697b851-4ccb-41c3-98c6-bdfa23f56b2d",
    "provider_used": "gemini",
    "model_used": "gemini-1.5-flash",
    "latency_ms": 1240
  }}
  ```

#### `GET /api/executions/{{id}}`
Fetches the complete execution trace, including Qdrant retrieval metrics, GitHub MCP tool invocations, and LLM fallback chain attempts.
"""
write_doc("docs/api.md", api_content)

# -----------------------------------------------------------------------------
# 6. docs/deployment.md
# -----------------------------------------------------------------------------
deploy_diag = """flowchart TD
    Internet((Public Internet)) --> Ingress[Ingress / Reverse Proxy :80/443]
    
    subgraph FrontendHosting [Frontend Deployment Options]
        Vercel[Vercel / Cloudflare Pages]
        NginxStatic[Dockerized Nginx Container]
    end

    subgraph BackendCluster [Backend Infrastructure]
        FastAPICluster[FastAPI Application Instances]
        WorkerCluster[Background Ingestion Workers]
    end

    subgraph ManagedData [Persistent Storage Layer]
        Postgres[(PostgreSQL 16 High-Availability)]
        Redis[(Redis 7 Cluster)]
        Qdrant[(Qdrant Vector Engine)]
    end

    Ingress -->|Route / | FrontendHosting
    Ingress -->|Route /api & /tracenest | FastAPICluster
    FastAPICluster --> ManagedData
    WorkerCluster --> ManagedData"""

deploy_content = f"""# RepoMind — Production Deployment Specification

## 1. Overview (In Plain Language)

Deploying RepoMind into production means taking it from your local computer and putting it onto a reliable cloud server so your whole team can use it anytime.

RepoMind supports two deployment models:
1. **Single-Node Docker Compose (Simplest)**: Everything runs together on one server (like an AWS EC2 instance, DigitalOcean Droplet, or Hetzner server).
2. **Distributed Cloud Architecture (Scalable)**: The frontend is hosted on a high-speed global content network (like Vercel or Cloudflare), while the backend API runs on a scalable container service (like AWS ECS, Google Cloud Run, or Render) backed by managed databases.

---

## 2. Production Topology Diagram

{make_mermaid_link(deploy_diag, "RepoMind Production Topology Diagram")}

---

## 3. Deployment Models

### 3.1 Model A: Single-Node Docker Compose (Recommended for POC)
Deploy all 9 services directly using Docker Compose behind an Nginx reverse proxy providing automatic SSL/TLS termination:

```bash
# 1. Clone on production host
git clone https://github.com/your-org/repomind.git /opt/repomind
cd /opt/repomind

# 2. Configure production environments
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env with production credentials and keys
# Set ENVIRONMENT=production and LOG_LEVEL=WARNING

# 3. Boot with restart policies
docker compose -f docker-compose.yml up -d --build
```

### 3.2 Model B: Distributed Hosting
- **Frontend SPA**: Built as static HTML/JS/CSS via `npm run build` and hosted on Vercel or Cloudflare Pages.
  - Set `VITE_API_BASE_URL=https://api.yourdomain.com`.
- **Backend API & Workers**: Containerized Docker image deployed to AWS ECS, Render, or Fly.io.
  - Set `CORS_ORIGINS=https://app.yourdomain.com`.
- **Databases**: Managed PostgreSQL (AWS RDS or Supabase) and Qdrant Cloud.
"""
write_doc("docs/deployment.md", deploy_content)

# -----------------------------------------------------------------------------
# 7. docs/testing.md
# -----------------------------------------------------------------------------
test_diag = """flowchart TD
    CodeCommit([Git Commit / PR]) --> CI[GitHub Actions CI]
    
    subgraph QualityGates [Automated Quality Verification]
        CI --> StaticChecks[TypeScript Strict Check & ESLint]
        CI --> StorybookBuild[Storybook Build Test :6006]
        CI --> BackendUnit[Pytest Backend Unit Tests]
        CI --> LiveDocker[Live Docker Pipeline Verification]
    end

    StaticChecks --> DeployApproval{All Gates Passed?}
    StorybookBuild --> DeployApproval
    BackendUnit --> DeployApproval
    LiveDocker --> DeployApproval

    DeployApproval -->|Yes| Success([Production Release Ready])
    DeployApproval -->|No| Block([Block Merge & Alert Developer])"""

test_content = f"""# RepoMind — Testing & Quality Assurance Specification

## 1. Overview (In Plain Language)

In RepoMind, "it compiles" is never considered proof that a feature works. 

We test software on three levels:
1. **Unit Tests**: Does this single function (like code chunking or secret redaction) behave correctly in isolation?
2. **Component Tests (Storybook)**: Does this button or chat box render properly in idle, loading, error, and success states?
3. **End-to-End Live Integration**: Does the entire 9-container system actually clone a real repository, save vectors to Qdrant, query GitHub via MCP, and return real answers with telemetry?

---

## 2. Testing Pyramid & Verification Gates

{make_mermaid_link(test_diag, "RepoMind Quality Verification Pipeline")}

---

## 3. Test Suites Reference

### 3.1 Live Docker Integration Pipeline (`backend/tests/test_live_docker.py`)
This test exercises the entire system running inside Docker:
- Verifies health check on `GET /health`.
- Creates a repository record via `POST /api/repositories`.
- Dispatches a background indexing job via `POST /api/repositories/{{id}}/index`.
- Polls indexing progress via `GET /api/repositories/{{id}}/status`.
- Submits an AI query via `POST /api/chat`.
- Validates that Qdrant vector retrieval, MCP tools, and LLM fallback executed.
- Inspects `GET /api/executions/{{id}}` to verify execution telemetry.
- Verifies that TraceNest recorded structured logs in `TraceNestLogs/`.

Run with:
```bash
python backend/tests/test_live_docker.py
```

### 3.2 Backend Pytest Suite (`backend/tests/`)
Covers unit-level behavior:
- AST code chunking syntax parsing for Python, JavaScript, TypeScript, Go, Java, Rust.
- Multi-provider LLM fallback logic.
- Secret redaction and masking safety.
- Qdrant payload serialization.

Run with:
```bash
pytest backend/tests -v
```

### 3.3 Storybook Verification
Validates that all 14 reusable components build without error:
```bash
cd frontend
npm run build-storybook
```
"""
write_doc("docs/testing.md", test_content)

print("Batch 1 generated successfully.")
