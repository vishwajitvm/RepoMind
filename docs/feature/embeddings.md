# Feature: Multi-Provider Embedding Router

## 1. Overview (In Plain Language)

An "embedding" is a mathematical summary of a piece of code. It converts words and symbols into a list of numbers (a vector) so that a computer can calculate how closely related two ideas are.

For example, an embedding engine knows that `def authenticate_user():` is closely related to the question *"How do users log in?"*, even though the exact words are different.

RepoMind includes an **EmbeddingRouter** that:
- Automatically uses an ultra-fast, local model (`all-MiniLM-L6-v2`) that requires no external API keys.
- Falls back to cloud providers like Google Gemini or OpenAI if configured.
- Guarantees vectors are compatible with our Qdrant vector database.

---

## 2. Embedding Generation Flow Diagram

![Multi-Provider Embedding Router Pipeline](https://mermaid.ink/svg/Zmxvd2NoYXJ0IFRECiAgICBJbnB1dENodW5rW0NvZGUgQ2h1bmsgVGV4dF0gLS0+IEVtYlJvdXRlcltFbWJlZGRpbmdSb3V0ZXIgRW5naW5lXQogICAgCiAgICBzdWJncmFwaCBQcm92aWRlcnMgW0VtYmVkZGluZyBQcm92aWRlcnMgUHJpb3JpdHldCiAgICAgICAgRW1iUm91dGVyIC0tPiBMb2NhbE1vZGVsWzEuIExvY2FsIFNlbnRlbmNlLVRyYW5zZm9ybWVyczogYWxsLU1pbmlMTS1MNi12Ml0KICAgICAgICBFbWJSb3V0ZXIgLS0+IEdlbWluaUVtYlsyLiBHb29nbGUgR2VtaW5pOiB0ZXh0LWVtYmVkZGluZy0wMDRdCiAgICAgICAgRW1iUm91dGVyIC0tPiBPbGxhbWFFbWJbMy4gTG9jYWwgT2xsYW1hOiBub21pYy1lbWJlZC10ZXh0XQogICAgICAgIEVtYlJvdXRlciAtLT4gT3BlbkFJRW1iWzQuIE9wZW5BSTogdGV4dC1lbWJlZGRpbmctMy1zbWFsbF0KICAgIGVuZAoKICAgIExvY2FsTW9kZWwgLS0+fERlbnNlIDM4NGQgVmVjdG9yfCBOb3JtYWxpemVbTDIgTm9ybWFsaXphdGlvbl0KICAgIEdlbWluaUVtYiAtLT58RGVuc2UgMzg0ZCBWZWN0b3J8IE5vcm1hbGl6ZQogICAgT2xsYW1hRW1iIC0tPnxEZW5zZSAzODRkIFZlY3RvcnwgTm9ybWFsaXplCiAgICBPcGVuQUlFbWIgLS0+fERlbnNlIDM4NGQgVmVjdG9yfCBOb3JtYWxpemUKCiAgICBOb3JtYWxpemUgLS0+IFFkcmFudEluZGV4WyhRZHJhbnQgVmVjdG9yIERhdGFiYXNlKV0=)

```mermaid
flowchart TD
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

    Normalize --> QdrantIndex[(Qdrant Vector Database)]
```

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
