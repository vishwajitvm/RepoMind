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
# 14. docs/feature/code-chunking.md
# -----------------------------------------------------------------------------
chunk_diag = """flowchart TD
    RawCode[Raw Source File] --> LangDetect{Detect Language}
    
    LangDetect -->|Python .py| PythonAST[Python AST Parser: ast.parse]
    LangDetect -->|TypeScript / JavaScript .ts/.tsx/.js| RegexParser[Symbol Extractor: classes, functions, types]
    LangDetect -->|Go / Rust / Java| MultiLangParser[Block & Indentation Parser]
    
    PythonAST --> ExtractPy[Extract Classes, Methods, Functions, Docstrings]
    RegexParser --> ExtractTS[Extract Components, Interfaces, Exported Symbols]
    MultiLangParser --> ExtractBlocks[Extract Logical Scopes & Line Spans]
    
    ExtractPy --> ChunkPayload[Structured Code Chunks + Line Ranges + Metadata]
    ExtractTS --> ChunkPayload
    ExtractBlocks --> ChunkPayload"""

chunk_content = f"""# Feature: Code-Aware Semantic Chunking

## 1. Overview (In Plain Language)

When standard search engines or simple AI tools read code, they often treat code like ordinary prose, cutting it into arbitrary 1,000-character blocks. This is disastrous for code because a function header might end up in one chunk while the function body ends up in another, destroying the logic.

RepoMind uses **Code-Aware Semantic Chunking**:
- It reads the code using the programming language's actual grammar rules.
- It identifies complete logical units—such as an entire Python class, a React component, or a TypeScript interface.
- It tracks the exact line numbers (e.g. lines 45 to 82) so you can always locate the exact source code.

---

## 2. Code Chunking Pipeline Diagram

{make_mermaid_link(chunk_diag, "Code-Aware Semantic Chunking Pipeline")}

---

## 3. Technical Architecture & Implementation

### 3.1 Python Abstract Syntax Tree (AST) Parsing
For Python files, RepoMind uses Python's standard `ast` module:
- Parses `ast.ClassDef`, `ast.FunctionDef`, and `ast.AsyncFunctionDef`.
- Preserves method hierarchy (`ClassName.method_name`).
- Extracts module-level docstrings as distinct architectural overview chunks.
- Preserves original indentation and exact 1-indexed `start_line` and `end_line`.

### 3.2 TypeScript / JavaScript Parsing
For JavaScript and TypeScript files:
- Detects `interface`, `type`, `class`, `export function`, and `React.FC` components.
- Scopes function boundaries using brace balancing and regex symbol detection.

### 3.3 Chunk Payload Metadata Schema
Every chunk emitted by the parser is enriched with metadata before vectorization:
```json
{{
  "path": "app/services/orchestrator.py",
  "language": "python",
  "symbol": "LangGraphOrchestrator.run",
  "chunk_type": "method",
  "start_line": 142,
  "end_line": 188,
  "repository_id": "cbee282e-bad2-4603-b556-9256fddf1b2f"
}}
```
"""
write_doc("docs/feature/code-chunking.md", chunk_content)

# -----------------------------------------------------------------------------
# 15. docs/feature/embeddings.md
# -----------------------------------------------------------------------------
emb_diag = """flowchart TD
    InputChunk[Code Chunk Text] --> EmbRouter[EmbeddingRouter Engine]
    
    subgraph Providers [Embedding Providers Priority]
        EmbRouter --> LocalModel[1. Local Sentence-Transformers: all-MiniLM-L6-v2]
        EmbRouter --> GeminiEmb[2. Google Gemini: text-embedding-004]
        EmbRouter --> OllamaEmb[3. Local Ollama: nomic-embed-text]
        EmbRouter --> OpenAIEmb[4. OpenAI: text-embedding-3-small]
    end

    LocalModel -->|Dense 384d Vector| Normalize[L2 Normalization]
    GeminiEmb -->|Dense 384d Vector| Normalize
    OllamaEmb -->|Dense 384d Vector| Normalize
    OpenAIEmb -->|Dense 384d Vector| Normalize

    Normalize --> QdrantIndex[(Qdrant Vector Database)]"""

emb_content = f"""# Feature: Multi-Provider Embedding Router

## 1. Overview (In Plain Language)

An "embedding" is a mathematical summary of a piece of code. It converts words and symbols into a list of numbers (a vector) so that a computer can calculate how closely related two ideas are.

For example, an embedding engine knows that `def authenticate_user():` is closely related to the question *"How do users log in?"*, even though the exact words are different.

RepoMind includes an **EmbeddingRouter** that:
- Automatically uses an ultra-fast, local model (`all-MiniLM-L6-v2`) that requires no external API keys.
- Falls back to cloud providers like Google Gemini or OpenAI if configured.
- Guarantees vectors are compatible with our Qdrant vector database.

---

## 2. Embedding Generation Flow Diagram

{make_mermaid_link(emb_diag, "Multi-Provider Embedding Router Pipeline")}

---

## 3. Technical Architecture

### 3.1 Responsibilities
- **Dimensional Uniformity**: Enforces a standard 384-dimensional vector format for seamless indexing in Qdrant collection `repomind_code_chunks`.
- **Batch Processing**: Groups code chunks into batches of 32 to maximize throughput and minimize CPU/GPU overhead.
- **Provider Resilience**: If a remote embedding provider times out or returns HTTP 429, the router automatically fails over to the local fallback without crashing the indexing worker.

### 3.2 Supported Providers
1. **Local (Default)**: Embedded fast transformer (`all-MiniLM-L6-v2`) running directly in the Python runtime.
2. **Google Gemini**: `text-embedding-004` via Google Generative AI REST API.
3. **Ollama**: `nomic-embed-text` served via Dockerized Ollama daemon.
4. **OpenAI**: `text-embedding-3-small` via OpenAI API.
"""
write_doc("docs/feature/embeddings.md", emb_content)

# -----------------------------------------------------------------------------
# 16. docs/feature/execution-trace.md
# -----------------------------------------------------------------------------
trace_diag = """flowchart TD
    UserQuery[User Question] --> Step1[1. Qdrant Semantic Retrieval]
    Step1 -->|Latency: 85ms / Chunks: 6| TraceRec1[Record Step 1 Telemetry]
    
    Step1 --> Step2[2. MCP Decision Logic]
    Step2 -->|Latency: 2ms / Live Check: False| TraceRec2[Record Step 2 Telemetry]
    
    Step2 --> Step3[3. LLM Router Generation]
    Step3 -->|Attempt 1: Gemini 401 Unauthorized / Latency: 120ms| Fallback1[Record Fallback Event]
    Fallback1 -->|Attempt 2: Groq 401 Unauthorized / Latency: 250ms| Fallback2[Record Fallback Event]
    Fallback2 -->|Attempt 3: Local Grounding 200 OK / Latency: 5ms| FallbackSuccess[Record Success Event]
    
    TraceRec1 --> Aggregate[Complete Execution Record]
    TraceRec2 --> Aggregate
    FallbackSuccess --> Aggregate
    
    Aggregate --> SaveDB[(Postgres executions table)]
    Aggregate --> SaveTN[(TraceNestLogs/YYYY-MM-DD.log)]
    Aggregate --> UIInspector[In-UI Step Timeline Inspector]"""

trace_content = f"""# Feature: In-UI Execution Trace & Timeline Inspector

## 1. Overview (In Plain Language)

AI systems should never be a black box. When RepoMind gives you an answer, you have the right to know exactly how that answer was generated:
- *What code files were retrieved from the database?*
- *Did the AI make a live call to GitHub to verify recent changes?*
- *Did Gemini fail and fall back to local Ollama?*
- *How many milliseconds did each step take?*

RepoMind's **Execution Trace Inspector** displays an interactive timeline right inside the chat window so you can inspect every single step and fallback event.

---

## 2. Execution Telemetry Pipeline Diagram

{make_mermaid_link(trace_diag, "Execution Telemetry Capture and Visualization")}

---

## 3. Technical Implementation

### 3.1 Trace Data Model
Every user question produces an immutable `Execution` record linked to the response message:
```json
{{
  "id": "4697b851-4ccb-41c3-98c6-bdfa23f56b2d",
  "message_id": "6fee9339-66f7-46b3-8eb4-6bf21a041477",
  "provider_used": "local_grounding",
  "model_used": "heuristic-v1",
  "latency_ms": 6182,
  "steps": [
    {{
      "name": "qdrant_retrieval",
      "status": "success",
      "latency_ms": 85,
      "details": {{"chunks_found": 6, "embedding_provider": "local"}}
    }},
    {{
      "name": "mcp_decision",
      "status": "success",
      "latency_ms": 2,
      "details": {{"triggered": false, "reason": "Indexed context sufficient"}}
    }},
    {{
      "name": "llm_routing_generation",
      "status": "success",
      "latency_ms": 6095,
      "details": {{"providers_attempted": 10, "fallback_occurred": true}}
    }}
  ]
}}
```

### 3.2 Dual Sink Persistence
1. **PostgreSQL**: Saved relationally in table `executions` for real-time frontend querying (`GET /api/executions/:id`).
2. **TraceNest Logs**: Serialized to structured JSON logs at `/app/TraceNestLogs/YYYY-MM-DD.log` for debugging via the TraceNest UI at `http://localhost:8000/tracenest/`.
"""
write_doc("docs/feature/execution-trace.md", trace_content)

# -----------------------------------------------------------------------------
# 17. docs/feature/github-mcp.md
# -----------------------------------------------------------------------------
mcp_diag = """flowchart TD
    Query[User Asks About Live Repository State] --> Decision{MCP Decision Engine}
    
    Decision -->|Indexed Context Sufficient| SkipMCP[Proceed Direct to LLM Synthesis]
    Decision -->|Requires Live / Recent Code| CallMCP[Invoke Backend MCP Client]
    
    subgraph DockerMCP [Official GitHub MCP Container]
        CallMCP -->|JSON-RPC via Docker Network| MCPServer[ghcr.io/github/github-mcp-server]
        MCPServer --> ToolSearch[Tool: search_code]
        MCPServer --> ToolContent[Tool: get_file_contents]
        ToolSearch --> GitHubAPI[GitHub REST / GraphQL API]
        ToolContent --> GitHubAPI
    end

    GitHubAPI --> MCPServer
    MCPServer -->|Live Fresh Code Content| LLMContext[LLM Prompt Assembly]
    SkipMCP --> LLMContext"""

mcp_content = f"""# Feature: Official GitHub MCP Integration

## 1. Overview (In Plain Language)

Codebases change constantly. If you indexed your repository yesterday, but an engineer pushed a bugfix this morning, an AI relying solely on indexed data might give an outdated answer.

RepoMind solves this using the **Model Context Protocol (MCP)**:
- RepoMind runs the official, secure GitHub MCP server in a Docker container.
- When a user asks about *"the latest commits"* or *"current changes"*, RepoMind queries GitHub live to inspect fresh files.
- It clearly tags citations as **Live Source** vs **Indexed Source** so you always know what data you are reading.

---

## 2. GitHub MCP Interaction Flow Diagram

{make_mermaid_link(mcp_diag, "Official GitHub MCP Server Integration")}

---

## 3. Technical Details

### 3.1 Standard Containerization
RepoMind uses the official GitHub MCP server image (`ghcr.io/github/github-mcp-server`) running as service `github-mcp` in `docker-compose.yml`:
- Communicates via JSON-RPC protocol over standard container interfaces.
- Authenticates using `GITHUB_PERSONAL_ACCESS_TOKEN` defined in `backend/.env`.

### 3.2 Read-Only Safety Boundary
To guarantee repository safety:
- Only read-only tools (`search_code`, `get_file_contents`) are permitted.
- Write tools (commit, push, branch creation, delete) are prohibited.
- If MCP credentials are not supplied or hit rate limits, the system fails gracefully back to indexed RAG context.
"""
write_doc("docs/feature/github-mcp.md", mcp_content)

# -----------------------------------------------------------------------------
# 18. docs/feature/llm-routing.md
# -----------------------------------------------------------------------------
llm_diag = """flowchart TD
    Prompt[Grounded Prompt & Context] --> Router[LLMRouter Engine]
    
    Router -->|Try 1| Gemini[Google Gemini 1.5 Flash]
    Gemini -->|Success| Complete([Return Grounded Response])
    Gemini -->|Failure 401 / 429| Groq[Try 2: Groq Llama-3.3 70B]
    
    Groq -->|Success| Complete
    Groq -->|Failure 401 / 429| Nvidia[Try 3: NVIDIA NIM Llama-3.3]
    
    Nvidia -->|Success| Complete
    Nvidia -->|Failure 401 / 429| OpenRouter[Try 4: OpenRouter Free Models]
    
    OpenRouter -->|Success| Complete
    OpenRouter -->|Failure 401 / 429| Mistral[Try 5: Mistral Small]
    
    Mistral -->|Success| Complete
    Mistral -->|Failure 401 / 429| DeepSeek[Try 6: DeepSeek Chat]
    
    DeepSeek -->|Success| Complete
    DeepSeek -->|Failure 401 / 429| Kimi[Try 7: Moonshot / Kimi]
    
    Kimi -->|Success| Complete
    Kimi -->|Failure 401 / 429| OpenAI[Try 8: OpenAI GPT-4o-mini]
    
    OpenAI -->|Success| Complete
    OpenAI -->|Failure 401 / 429| Ollama[Try 9: Ollama Local Daemon :11434]
    
    Ollama -->|Success| Complete
    Ollama -->|Failure / Offline| LocalGround[Try 10: Local Grounding Engine]
    LocalGround --> Complete"""

llm_content = f"""# Feature: 10-Tier Multi-Provider LLM Router

## 1. Overview (In Plain Language)

Cloud AI providers are notorious for unexpected downtime, rate limits (HTTP 429 errors), and quota expirations. If an application only connects to a single AI provider, your team is completely blocked when that provider experiences an outage.

RepoMind solves this with a **10-Tier LLM Router**:
- It attempts the fastest, most cost-effective cloud AI first.
- If that provider fails, it seamlessly tries the next provider in milliseconds.
- If the entire internet is down or all cloud API keys are empty, it falls back to a **local AI running inside Docker on your machine via Ollama**.
- If even Ollama is unavailable, RepoMind's **Local Grounding Engine** synthesizes the exact retrieved code chunks so you always receive an answer.

---

## 2. 10-Tier Failover State Machine Diagram

{make_mermaid_link(llm_diag, "10-Tier Multi-Provider Fallback State Machine")}

---

## 3. Technical Architecture

### 3.1 Provider Adapter Pattern
All LLM providers implement a unified interface:
```python
class BaseLLMAdapter(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.2
    ) -> str:
        pass
```

### 3.2 10-Tier Sequence Order
1. **Google Gemini Flash**: Ultra-low latency, generous free tier.
2. **Groq**: High-throughput Llama-3.3 70B inference.
3. **NVIDIA NIM**: Enterprise-grade Llama-3.3 models.
4. **OpenRouter**: Aggregated multi-model gateway.
5. **Mistral AI**: Fast European inference models.
6. **DeepSeek**: High-performance reasoning models.
7. **Moonshot / Kimi**: Long-context reasoning.
8. **OpenAI**: GPT-4o-mini fallback.
9. **Ollama**: Local Docker daemon running offline models.
10. **Local Grounding Engine**: Heuristic deterministic code synthesizer.
"""
write_doc("docs/feature/llm-routing.md", llm_content)

# -----------------------------------------------------------------------------
# 19. docs/feature/rag-chat.md
# -----------------------------------------------------------------------------
rag_diag = """flowchart TD
    UserQuery[User Question] --> EmbedQuery[EmbeddingRouter: Convert query to 384d vector]
    EmbedQuery --> QdrantSearch[Qdrant: Cosine similarity search]
    QdrantSearch --> TopChunks[Top-K Code Chunks with line bounds]
    TopChunks --> MCPCheck{Live GitHub Check Needed}
    MCPCheck -->|Yes| FetchMCP[Fetch current file contents via GitHub MCP]
    MCPCheck -->|No| CombineContext[Assemble Grounded Code Context]
    FetchMCP --> CombineContext
    CombineContext --> LLMRouting[LLMRouter Multi-Provider Synthesis]
    LLMRouting --> AnswerSynthesis[Answer Generated with Grounded Citations]"""

rag_content = f"""# Feature: Retrieval-Augmented Generation (RAG) Chat

## 1. Overview (In Plain Language)

Standard AI models only know what they were trained on in the past. They have no idea what code is inside your private repository today.

**Retrieval-Augmented Generation (RAG)** is the technique RepoMind uses to solve this:
1. When you ask a question, RepoMind searches your codebase for the most relevant functions and classes.
2. It gathers those specific code snippets and feeds them into the AI alongside your question.
3. The AI reads the actual code and answers based strictly on reality, citing exact file names and line numbers.

---

## 2. RAG Retrieval & Synthesis Pipeline Diagram

{make_mermaid_link(rag_diag, "RepoMind RAG Retrieval and Answer Synthesis Pipeline")}

---

## 3. Technical Architecture

### 3.1 LangGraph Orchestrator
The RAG workflow is coordinated using a compiled LangGraph `StateGraph`:
- **Node `qdrant_retrieval`**: Embeds query vector and runs similarity retrieval filtered by `repository_id`.
- **Node `mcp_decision`**: Analyzes question keywords (e.g. "latest", "current", "fresh", "commit") and chunk freshness.
- **Node `mcp_execution`**: Invokes the official GitHub MCP server when live code verification is demanded.
- **Node `llm_routing_generation`**: Injects retrieved code into a strict system prompt instructing the model to cite exact line spans.

### 3.2 Grounded Citation Verification
Every response contains structured citation objects:
```json
{{
  "file_path": "backend/app/main.py",
  "symbol": "app",
  "start_line": 35,
  "end_line": 56,
  "source_type": "indexed"
}}
```
"""
write_doc("docs/feature/rag-chat.md", rag_content)

# -----------------------------------------------------------------------------
# 20. docs/feature/repository-indexing.md
# -----------------------------------------------------------------------------
index_diag = """flowchart TD
    Register[POST /api/repositories/:id/index] --> Enqueue[Push Job to Redis Queue]
    Enqueue --> Worker[Ingestion Worker Dequeues Job]
    
    Worker --> ShallowClone[git clone --depth 1 into isolated temp directory]
    ShallowClone --> ScanFiles[Scan directory tree & apply ignore filters]
    
    subgraph FileLoop [Per-File Error Isolation Loop]
        ScanFiles --> ReadFile[Read Source File]
        ReadFile --> ASTParse[AST Code-Aware Chunking]
        ASTParse --> BatchEmbed[Generate 384d Vectors via EmbeddingRouter]
        BatchEmbed --> SaveQdrant[Upsert Vectors into Qdrant]
        SaveQdrant --> SavePostgres[Insert File & Symbol Record in PostgreSQL]
    end

    FileLoop --> Cleanup[Remove Temp Directory]
    Cleanup --> MarkComplete[Set Job Status = completed in PostgreSQL]"""

index_content = f"""# Feature: Resumable Repository Indexing

## 1. Overview (In Plain Language)

Indexing a large software repository requires downloading files, parsing thousands of lines of code, and calculating mathematical embeddings. If you tried to do all of this during a single web request, your browser would freeze and time out.

RepoMind's **Repository Indexing Engine**:
- Runs in the background using Redis and a dedicated worker process.
- Processes files with **isolated error boundaries**: if a single corrupted file has a syntax error, RepoMind records the error for that file and keeps indexing the rest of the repository without stopping.
- Automatically ignores useless files like `node_modules/`, `.git/`, and `.env` secrets.

---

## 2. Background Ingestion Pipeline Diagram

{make_mermaid_link(index_diag, "Resumable Background Indexing Workflow")}

---

## 3. Technical Architecture

### 3.1 Ingestion Flow
1. **Trigger**: Client issues `POST /api/repositories/:id/index`. FastAPI creates an `indexing_jobs` row in PostgreSQL and pushes the job ID to Redis.
2. **Shallow Clone**: The worker performs a fast Git shallow clone (`git clone --depth 1`).
3. **Filtering**: The worker ignores build directories, binaries, and secrets.
4. **AST Chunking**: Source files are parsed into semantic chunks.
5. **Embedding & Storage**: Vectors are upserted to Qdrant, and relational metadata is written to PostgreSQL.
6. **Completion**: Temporary disk storage is purged, and the job status is set to `completed`.
"""
write_doc("docs/feature/repository-indexing.md", index_content)

print("Batch 3 generated successfully.")
