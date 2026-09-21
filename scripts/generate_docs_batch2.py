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
# 8. docs/troubleshooting.md
# -----------------------------------------------------------------------------
trouble_diag = """flowchart TD
    Start([Encountered Issue]) --> CheckEndpoint{What failed?}
    
    CheckEndpoint -->|HTTP 404 on /tracenest| SlashFix[Check Trailing Slash: visit /tracenest/ instead]
    CheckEndpoint -->|CORS Error in Browser| CorsFix[Check CORS_ORIGINS in backend/.env includes frontend host]
    CheckEndpoint -->|PostgreSQL Connection Error| DbFix[Check repomind-postgres health: pg_isready]
    CheckEndpoint -->|Qdrant Search Empty| QdrantFix[Verify collection repomind_code_chunks dimension is 384]
    CheckEndpoint -->|Ollama 404 Not Found| OllamaFix[Execute: docker exec -it repomind-ollama ollama pull deepseek-r1:1.5b]
    CheckEndpoint -->|GitHub MCP Rate Limit| McpFix[Verify GITHUB_PERSONAL_ACCESS_TOKEN in backend/.env]"""

trouble_content = f"""# RepoMind — Troubleshooting Guide

## 1. Overview (In Plain Language)

When developing or running a complex multi-container application, problems can occasionally occur: a service might take too long to start, a network port might be blocked, or an AI provider might be experiencing downtime.

This guide provides direct, step-by-step diagnostic procedures to quickly identify root causes and resolve issues without guesswork.

---

## 2. Interactive Troubleshooting Decision Tree

{make_mermaid_link(trouble_diag, "RepoMind Troubleshooting Decision Tree")}

---

## 3. Common Issues & Solutions

### 3.1 TraceNest UI Returns 404 or Assets Do Not Load
- **Cause**: TraceNest assets (`styles.css`, `app.js`) are served relative to the dashboard directory.
- **Solution**:
  - Visit [http://localhost:8000/tracenest/](http://localhost:8000/tracenest/) (note the trailing slash).
  - RepoMind automatically redirects `/tracenest` to `/tracenest/` and registers root fallbacks.
  - Verify that `repomind-backend` is running and healthy.

### 3.2 Ollama Fallback Fails with 404 Not Found
- **Cause**: The local Ollama container does not have the target model downloaded yet.
- **Solution**:
  ```bash
  docker exec -it repomind-ollama ollama pull deepseek-r1:1.5b
  ```
  *Note*: RepoMind's `LocalGroundingAdapter` automatically takes over if Ollama is unconfigured or downloading.

### 3.3 Database Connection Refused (`postgresql://...`)
- **Cause**: PostgreSQL has not finished its first-time database initialization.
- **Solution**:
  ```bash
  docker compose ps postgres
  # Wait until status changes to "healthy"
  docker logs repomind-postgres
  ```

### 3.4 Browser Shows CORS Network Error
- **Cause**: The React frontend origin is not in the allowed CORS list in `backend/.env`.
- **Solution**:
  Ensure `CORS_ORIGINS` in `backend/.env` includes your browser URL:
  ```env
  CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
  ```
"""
write_doc("docs/troubleshooting.md", trouble_content)

# -----------------------------------------------------------------------------
# 9. docs/security.md
# -----------------------------------------------------------------------------
sec_diag = """flowchart TD
    subgraph IngestionBoundary [Ingestion Security Boundary]
        RawRepo[Repository Files] --> SecretScanner[Regex & Name Secret Scanner]
        SecretScanner -->|.env / id_rsa / tokens| Discard([Blocked & Ignored])
        SecretScanner -->|Clean Code Chunks| Embedder[Vector Indexer]
    end

    subgraph LoggingBoundary [Telemetry Redaction Boundary]
        InternalEvents[API & Execution Events] --> Redactor[TraceNest Secret Redactor]
        Redactor -->|Keys / Passwords / Auth| Mask[Masked to ********]
        Redactor -->|Safe Metadata| LogFiles[TraceNestLogs/YYYY-MM-DD.log]
    end

    subgraph MCPBoundary [GitHub MCP Boundary]
        MCPCall[MCP Invocations] --> ReadOnlyFilter[Read-Only Tool Filter]
        ReadOnlyFilter -->|search_code & get_file| Allowed[Execute MCP Read]
        ReadOnlyFilter -->|Write / Push / Merge| Denied([Blocked & Prohibited])
    end"""

sec_content = f"""# RepoMind — Security Architecture Specification

## 1. Overview (In Plain Language)

Security in RepoMind is designed with **defense in depth**:
1. **Zero Secret Leaks**: The system automatically redacts API keys, tokens, and passwords from logs and web screens.
2. **Never Index Secrets**: Files containing private keys, credentials, or `.env` configs are discarded before indexing.
3. **Read-Only GitHub Access**: RepoMind can only read code from GitHub. It is physically blocked from modifying repositories, creating commits, or changing settings.
4. **Environment Isolation**: Private database credentials and AI keys never touch the web browser.

---

## 2. Security Boundaries Diagram

{make_mermaid_link(sec_diag, "RepoMind Multi-Tier Security Boundaries")}

---

## 3. Strict Security Policies

### 3.1 Secret Redaction in Telemetry & Observability
TraceNest and LangSmith tracing run through an automated redaction barrier (`tracenest.security.redaction`):
- Any metadata key matching `["password", "secret", "token", "api_key", "auth", "key"]` is masked to `[REDACTED]` or `********`.
- Raw authorization headers are stripped before telemetry serialization.

### 3.2 Ignored & Blocked File Patterns
The background ingestion worker ignores sensitive and build-related paths:
```text
.git, node_modules, dist, build, coverage, .venv, __pycache__,
.env, .env.*, credentials.json, id_rsa, id_ed25519, *.pem, *.key
```

### 3.3 Strict Read-Only GitHub MCP Boundary
Only read-only MCP tools are enabled:
- `search_code`: Search code symbols and snippets across the repository.
- `get_file_contents`: Retrieve current, authoritative file content for line-grounded reasoning.
- All write, commit, delete, or administrative tools are explicitly excluded.
"""
write_doc("docs/security.md", sec_content)

# -----------------------------------------------------------------------------
# 10. docs/observability.md
# -----------------------------------------------------------------------------
obs_diag = """flowchart LR
    subgraph RequestFlow [FastAPI Execution]
        Req[Client Request] --> MW[TraceNestMiddleware]
        MW --> Handler[API Route Handler]
        Handler --> Tracer[ObservabilityTracer]
    end

    subgraph TelemetrySink [Telemetry Sinks]
        MW -->|HTTP Latency & Status| TNLogger[TraceNest Logger]
        Tracer -->|Custom Execution Events| TNLogger
        Tracer -->|Graph Traces| LangSmith[LangSmith Cloud API]
    end

    subgraph UserSurfaces [Observability Dashboards]
        TNLogger -->|Buffered JSON Lines| LogFile[(TraceNestLogs/*.log)]
        LogFile --> TraceNestUI[TraceNest Dashboard :8000/tracenest/]
        Handler --> InUIInspector[In-UI Execution Timeline Inspector]
    end"""

obs_content = f"""# RepoMind — Observability & Telemetry Specification

## 1. Overview (In Plain Language)

When an AI system operates behind the scenes, developers need to know:
- *Which AI model actually answered my question?*
- *Did the cloud provider fail and fall back to local Ollama?*
- *How long did the vector search in Qdrant take?*
- *What files were retrieved?*

RepoMind provides full transparency through an integrated observability stack:
1. **TraceNest Dashboard**: A built-in web dashboard at `http://localhost:8000/tracenest` showing real-time logs, response times, and system events.
2. **In-UI Execution Inspector**: An interactive step-by-step timeline inside the chat window showing every stage of processing.
3. **LangSmith Integration**: Deep distributed tracing for multi-step LangGraph agent workflows.

---

## 2. Telemetry Pipeline Diagram

{make_mermaid_link(obs_diag, "RepoMind Observability and Telemetry Pipeline")}

---

## 3. Telemetry Systems Reference

### 3.1 TraceNest UI & Logging (`http://localhost:8000/tracenest`)
- **Location**: Hosted directly by FastAPI at `/tracenest/`.
- **Log Files**: Stored in `TraceNestLogs/YYYY-MM-DD.log` as structured, single-line JSON records.
- **Middleware**: `TraceNestMiddleware` automatically captures:
  - Client IP, HTTP method, and path.
  - Duration in milliseconds (`duration_ms`).
  - HTTP status codes and sanitized header maps.
- **Event Logging**: Ingestion milestones, Qdrant retrieval stats, and LLM fallback events are recorded via `ObservabilityTracer`.

### 3.2 In-UI Execution Timeline
Whenever a chat question is submitted, the API returns an `execution_id`. The frontend displays an interactive visual timeline showing:
- **`qdrant_retrieval`**: Chunks found, embedding provider used, latency in ms.
- **`mcp_decision`**: Deterministic decision on whether live repository inspection was triggered.
- **`llm_routing_generation`**: Every provider attempted, individual error messages (e.g. 401 Unauthorized or 429 Rate Limit), and the winning provider.

### 3.3 LangSmith Distributed Tracing
When `LANGSMITH_API_KEY` is configured in `backend/.env`, all LangGraph agent steps are mirrored to LangSmith. Telemetry failures are strictly non-fatal and will never crash the application.
"""
write_doc("docs/observability.md", obs_content)

# -----------------------------------------------------------------------------
# 11. docs/frontend.md
# -----------------------------------------------------------------------------
front_diag = """flowchart TD
    subgraph UIComponents [Component Layer]
        App[App Shell & Layout]
        RepoSelector[RepositorySelector Component]
        ChatArea[ChatInput & ChatMessage]
        Timeline[ExecutionStep & ToolCall Inspector]
    end

    subgraph StateAndData [State Management & Data Layer]
        TanStack[TanStack Query Cache]
        ZodForms[React Hook Form + Zod Validation]
        LocalState[Local UI State]
    end

    subgraph RemoteAPI [Backend Communication]
        ApiClient[Axios / Fetch API Client]
        BackendAPI[FastAPI Backend :8000]
    end

    App --> RepoSelector
    App --> ChatArea
    App --> Timeline

    RepoSelector --> TanStack
    ChatArea --> ZodForms
    ZodForms --> TanStack
    TanStack --> ApiClient
    ApiClient --> BackendAPI"""

front_content = f"""# RepoMind — Frontend Architecture Specification

## 1. Overview (In Plain Language)

The RepoMind frontend is a fast, responsive Single-Page Application (SPA) designed to feel like a modern developer workbench.

Instead of reloading the entire web page on every interaction:
- The app updates instantly when you select repositories or submit questions.
- It displays live progress indicators during indexing.
- It provides rich code snippet previews with exact line numbers and syntax formatting.
- It renders an interactive timeline showing the AI's step-by-step thinking process.

---

## 2. Frontend Component Hierarchy & State Flow

{make_mermaid_link(front_diag, "Frontend Component Hierarchy and State Flow")}

---

## 3. Technical Architecture

### 3.1 Stack
- **Framework**: React 18 with Vite for lightning-fast Hot Module Replacement (HMR).
- **Type Safety**: Strict TypeScript (`noImplicitAny: true`, strict null checks).
- **Styling**: Tailwind CSS with custom utility composition and full dark/light theme support.
- **Server State**: TanStack Query (React Query) for querying, mutations, and caching.
- **Form Management**: React Hook Form with Zod schemas for runtime schema validation.

### 3.2 Key UI Components
- **`RepositorySelector`**: Controlled dropdown allowing quick switching between indexed repositories with status indicators.
- **`ChatInput` & `ChatMessage`**: Keyboard-accessible chat interface with Markdown rendering and code syntax highlighting.
- **`SourceCitation`**: Grounded citation pill displaying file path, symbol, line range, and source type (Indexed vs Live GitHub).
- **`ExecutionStep` & `ToolCall`**: Collapsible execution trace cards showing latency, tool arguments, and provider fallback status.
"""
write_doc("docs/frontend.md", front_content)

# -----------------------------------------------------------------------------
# 12. docs/storybook.md
# -----------------------------------------------------------------------------
sb_diag = """flowchart LR
    subgraph ComponentSources [UI Component Code]
        Base[Base Components: Button / Input / Modal / Toast]
        Domain[Domain Components: ChatMessage / ToolCall / Citations]
    end

    subgraph StoriesSuite [Storybook Story Catalog]
        Stories[56 Interactive Component Stories]
        Controls[Storybook Controls & Args]
    end

    subgraph Runtime [Containerized Storybook :6006]
        ViteDev[Vite Storybook Server]
        Browser[Developer Web Browser]
    end

    Base --> Stories
    Domain --> Stories
    Stories --> Controls
    Controls --> ViteDev
    ViteDev --> Browser"""

sb_content = f"""# RepoMind — Storybook UI Catalog & Workbench

## 1. Overview (In Plain Language)

Storybook is an interactive design catalog and testing workbench for RepoMind's visual components.

Think of it as a showroom where every single button, text input, modal popup, and chat bubble is displayed in all of its different modes (idle, loading, error, success) in complete isolation, without needing the backend or databases to be running.

---

## 2. Storybook Architecture Diagram

{make_mermaid_link(sb_diag, "Storybook Isolated Component Architecture")}

---

## 3. Containerized Storybook Service

Storybook runs as a dedicated Docker Compose service (`repomind-storybook`) on port `6006`:
- **URL**: [http://localhost:6006](http://localhost:6006)
- **Container**: `repomind-storybook`

---

## 4. Reusable Component Catalog (14 Components / 56 Stories)

### 4.1 Base Foundation Components
1. **`Button`**: Supports variants (`primary`, `secondary`, `outline`, `ghost`, `danger`), sizes (`sm`, `md`, `lg`), loading spinner states, and icon positioning.
2. **`Input`**: Text input with label, helper text, error states, and left/right icon slots.
3. **`Select`**: Custom styled dropdown selector with typed option lists.
4. **`Textarea`**: Auto-resizing multi-line text input with character limit indicators.
5. **`Badge`**: Status badge supporting `default`, `success`, `warning`, `danger`, and `info` colorways.
6. **`Modal`**: Accessible dialog overlay with backdrop blur, keyboard dismissal (Escape), and customizable action buttons.
7. **`Toast`**: Notification banners with timeout animations and dismiss controls.
8. **`Spinner`**: Animated loading spinner supporting multiple sizes and colors.

### 4.2 AI & Codebase Domain Components
9. **`ChatInput`**: Interactive multi-line message composer with submit shortcuts (Enter / Shift+Enter).
10. **`ChatMessage`**: Markdown-capable message bubble rendering user queries and assistant responses with grounded citations.
11. **`ToolCall`**: Collapsible execution card showing tool names (`search_code`, `get_file_contents`), arguments, and output status.
12. **`ExecutionStep`**: Step card displaying pipeline progress (`qdrant_retrieval`, `mcp_decision`, `llm_routing_generation`) with latency badges.
13. **`RepositorySelector`**: In-header repository picker with branch badges and indexing status pills.
14. **`SourceCitation`**: Grounded reference badge indicating file path, symbol, line bounds, and live vs. indexed provenance.

---

## 5. Verification Command
To verify that all stories compile without headless browser errors:
```bash
cd frontend
npm run build-storybook
```
"""
write_doc("docs/storybook.md", sb_content)

# -----------------------------------------------------------------------------
# 13. docs/data-model.md
# -----------------------------------------------------------------------------
data_diag = """erDiagram
    REPOSITORIES ||--o{ FILES : contains
    REPOSITORIES ||--o{ INDEXING_JOBS : tracks
    REPOSITORIES ||--o{ CONVERSATIONS : scopes
    CONVERSATIONS ||--o{ MESSAGES : contains
    MESSAGES ||--o| EXECUTIONS : generates
    FILES ||--o{ QDRANT_CHUNKS : "vectorized into"

    REPOSITORIES {
        uuid id PK
        string name
        string url
        string branch
        string status
        timestamp created_at
    }

    FILES {
        uuid id PK
        uuid repository_id FK
        string path
        string language
        int size_bytes
        string content_hash
    }

    INDEXING_JOBS {
        uuid id PK
        uuid repository_id FK
        string status
        int files_indexed
        int chunks_created
        string error
    }

    CONVERSATIONS {
        uuid id PK
        uuid repository_id FK
        string title
        timestamp created_at
    }

    MESSAGES {
        uuid id PK
        uuid conversation_id FK
        string role
        text content
        jsonb citations
    }

    EXECUTIONS {
        uuid id PK
        uuid message_id FK
        string provider_used
        string model_used
        int latency_ms
        jsonb steps
        jsonb fallback_chain
    }

    QDRANT_CHUNKS {
        uuid point_id PK
        vector embedding_384d
        string repository_id
        string file_path
        string symbol
        string chunk_type
        int start_line
        int end_line
    }"""

data_content = f"""# RepoMind — Data Model & Storage Architecture

## 1. Overview (In Plain Language)

RepoMind stores data across two specialized database systems:
1. **PostgreSQL (The Filing Cabinet)**: Remembers your project details, chat history, indexing job statuses, and execution traces.
2. **Qdrant (The Semantic Search Engine)**: Stores mathematical vectors representing code snippets, allowing RepoMind to find relevant code by meaning rather than simple keyword matches.

---

## 2. Entity-Relationship & Vector Schema Diagram

{make_mermaid_link(data_diag, "RepoMind Relational ERD and Vector Payload Schema")}

---

## 3. Database Schemas

### 3.1 PostgreSQL Relational Tables (SQLAlchemy 2.0)
- **`repositories`**: Stores registered GitHub repositories, target branches, and current ingestion status.
- **`files`**: Catalogs repository file trees, programming languages, and SHA-256 content hashes.
- **`indexing_jobs`**: Records background worker job progression, file counts, and error messages.
- **`conversations`**: Thread grouping for user chat sessions scoped to specific repositories.
- **`messages`**: Individual user queries and assistant responses with grounded citations.
- **`executions`**: Complete telemetry snapshots capturing providers attempted, latencies, and tool calls.

### 3.2 Qdrant Vector Collection (`repomind_code_chunks`)
- **Metric**: Cosine similarity (`Distance.COSINE`).
- **Dimensions**: 384 dimensions (matching `all-MiniLM-L6-v2` dense embeddings).
- **Payload Metadata**:
  ```json
  {{
    "repository_id": "cbee282e-bad2-4603-b556-9256fddf1b2f",
    "path": "app/services/indexer.py",
    "language": "python",
    "symbol": "CodeIndexer.index_repository",
    "chunk_type": "method",
    "start_line": 45,
    "end_line": 95,
    "content_hash": "a3f891b2c4e..."
  }}
  ```
"""
write_doc("docs/data-model.md", data_content)

print("Batch 2 generated successfully.")
