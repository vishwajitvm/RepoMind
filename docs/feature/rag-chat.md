# Feature: Retrieval-Augmented Generation (RAG) Chat

## 1. Overview (In Plain Language)

Standard AI models only know what they were trained on in the past. They have no idea what code is inside your private repository today.

**Retrieval-Augmented Generation (RAG)** is the technique RepoMind uses to solve this:
1. When you ask a question, RepoMind searches your codebase for the most relevant functions and classes.
2. It gathers those specific code snippets and feeds them into the AI alongside your question.
3. The AI reads the actual code and answers based strictly on reality, citing exact file names and line numbers.

---

## 2. RAG Retrieval & Synthesis Pipeline Diagram

![RepoMind RAG Retrieval and Answer Synthesis Pipeline](https://mermaid.ink/svg/Zmxvd2NoYXJ0IFRECiAgICBVc2VyUXVlcnlbVXNlciBRdWVzdGlvbjogV2hlcmUgaXMgYXV0aCB2YWxpZGF0ZWQ/XSAtLT4gRW1iZWRRdWVyeVtFbWJlZGRpbmdSb3V0ZXI6IENvbnZlcnQgcXVlcnkgdG8gMzg0ZCB2ZWN0b3JdCiAgICBFbWJlZFF1ZXJ5IC0tPiBRZHJhbnRTZWFyY2hbUWRyYW50OiBDb3NpbmUgc2ltaWxhcml0eSBzZWFyY2ggd2l0aCByZXBvc2l0b3J5X2lkIGZpbHRlcl0KICAgIAogICAgUWRyYW50U2VhcmNoIC0tPiBUb3BDaHVua3NbVG9wLUsgQ29kZSBDaHVua3M6IGZpbGUgcGF0aCwgc3ltYm9sLCBsaW5lIGJvdW5kc10KICAgIFRvcENodW5rcyAtLT4gTUNQQ2hlY2t7SXMgTGl2ZSBDb2RlIFZlcmlmaWNhdGlvbiBOZWVkZWQ/fQogICAgCiAgICBNQ1BDaGVjayAtLT58WWVzfCBGZXRjaE1DUFtGZXRjaCBjdXJyZW50IGZpbGUgY29udGVudHMgdmlhIEdpdEh1YiBNQ1BdCiAgICBNQ1BDaGVjayAtLT58Tm98IENvbWJpbmVDb250ZXh0W0Fzc2VtYmxlIFN5c3RlbSBQcm9tcHQgKyBHcm91bmRlZCBDb2RlIENvbnRleHRdCiAgICBGZXRjaE1DUCAtLT4gQ29tYmluZUNvbnRleHQKICAgIAogICAgQ29tYmluZUNvbnRleHQgLS0+IExMTVJvdXRpbmdbTExNUm91dGVyIE11bHRpLVByb3ZpZGVyIFN5bnRoZXNpc10KICAgIExMTVJvdXRpbmcgLS0+IEFuc3dlclN5bnRoZXNpc1tBbnN3ZXIgR2VuZXJhdGVkIHdpdGggR3JvdW5kZWQgTGluZSBDaXRhdGlvbnNd)

```mermaid
flowchart TD
    UserQuery[User Question: Where is auth validated?] --> EmbedQuery[EmbeddingRouter: Convert query to 384d vector]
    EmbedQuery --> QdrantSearch[Qdrant: Cosine similarity search with repository_id filter]
    
    QdrantSearch --> TopChunks[Top-K Code Chunks: file path, symbol, line bounds]
    TopChunks --> MCPCheck{Is Live Code Verification Needed?}
    
    MCPCheck -->|Yes| FetchMCP[Fetch current file contents via GitHub MCP]
    MCPCheck -->|No| CombineContext[Assemble System Prompt + Grounded Code Context]
    FetchMCP --> CombineContext
    
    CombineContext --> LLMRouting[LLMRouter Multi-Provider Synthesis]
    LLMRouting --> AnswerSynthesis[Answer Generated with Grounded Line Citations]
```

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
{
  "file_path": "backend/app/main.py",
  "symbol": "app",
  "start_line": 35,
  "end_line": 56,
  "source_type": "indexed"
}
```
