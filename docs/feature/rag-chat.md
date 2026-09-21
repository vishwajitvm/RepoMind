# Feature: Retrieval-Augmented Generation (RAG) Chat

## 1. Overview (In Plain Language)

Standard AI models only know what they were trained on in the past. They have no idea what code is inside your private repository today.

**Retrieval-Augmented Generation (RAG)** is the technique RepoMind uses to solve this:
1. When you ask a question, RepoMind searches your codebase for the most relevant functions and classes.
2. It gathers those specific code snippets and feeds them into the AI alongside your question.
3. The AI reads the actual code and answers based strictly on reality, citing exact file names and line numbers.

---

## 2. RAG Retrieval & Synthesis Pipeline Diagram

![RepoMind RAG Retrieval and Answer Synthesis Pipeline](https://mermaid.ink/svg/Zmxvd2NoYXJ0IFRECiAgICBVc2VyUXVlcnlbVXNlciBRdWVzdGlvbl0gLS0+IEVtYmVkUXVlcnlbRW1iZWRkaW5nUm91dGVyOiBDb252ZXJ0IHF1ZXJ5IHRvIDM4NGQgdmVjdG9yXQogICAgRW1iZWRRdWVyeSAtLT4gUWRyYW50U2VhcmNoW1FkcmFudDogQ29zaW5lIHNpbWlsYXJpdHkgc2VhcmNoXQogICAgUWRyYW50U2VhcmNoIC0tPiBUb3BDaHVua3NbVG9wLUsgQ29kZSBDaHVua3Mgd2l0aCBsaW5lIGJvdW5kc10KICAgIFRvcENodW5rcyAtLT4gTUNQQ2hlY2t7TGl2ZSBHaXRIdWIgQ2hlY2sgTmVlZGVkfQogICAgTUNQQ2hlY2sgLS0+fFllc3wgRmV0Y2hNQ1BbRmV0Y2ggY3VycmVudCBmaWxlIGNvbnRlbnRzIHZpYSBHaXRIdWIgTUNQXQogICAgTUNQQ2hlY2sgLS0+fE5vfCBDb21iaW5lQ29udGV4dFtBc3NlbWJsZSBHcm91bmRlZCBDb2RlIENvbnRleHRdCiAgICBGZXRjaE1DUCAtLT4gQ29tYmluZUNvbnRleHQKICAgIENvbWJpbmVDb250ZXh0IC0tPiBMTE1Sb3V0aW5nW0xMTVJvdXRlciBNdWx0aS1Qcm92aWRlciBTeW50aGVzaXNdCiAgICBMTE1Sb3V0aW5nIC0tPiBBbnN3ZXJTeW50aGVzaXNbQW5zd2VyIEdlbmVyYXRlZCB3aXRoIEdyb3VuZGVkIENpdGF0aW9uc10=)

```mermaid
flowchart TD
    UserQuery[User Question] --> EmbedQuery[EmbeddingRouter: Convert query to 384d vector]
    EmbedQuery --> QdrantSearch[Qdrant: Cosine similarity search]
    QdrantSearch --> TopChunks[Top-K Code Chunks with line bounds]
    TopChunks --> MCPCheck{Live GitHub Check Needed}
    MCPCheck -->|Yes| FetchMCP[Fetch current file contents via GitHub MCP]
    MCPCheck -->|No| CombineContext[Assemble Grounded Code Context]
    FetchMCP --> CombineContext
    CombineContext --> LLMRouting[LLMRouter Multi-Provider Synthesis]
    LLMRouting --> AnswerSynthesis[Answer Generated with Grounded Citations]
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
