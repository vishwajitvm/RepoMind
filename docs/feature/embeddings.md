# Feature: Embedding Router & Dense Vector Storage

## Purpose
Decouples vector embedding generation from individual providers and protects against network outages or rate limits with automatic failover.

## Providers & Priority
1. **Google Gemini**: `text-embedding-004` (when `GEMINI_API_KEY` is configured).
2. **Ollama**: `nomic-embed-text` or `all-minilm` (when `OLLAMA_BASE_URL` is active).
3. **Local Deterministic Fallback**: Normalized 384-dimensional unit-norm projection, ensuring offline operation without paid keys or GPUs.

## Qdrant Integration
- Vectors are stored in collection `repomind_code_chunks` with Cosine distance.
- Payloads carry `repository_id`, `path`, `symbol`, `start_line`, `end_line`, and `content`.
- Search supports repository-level keyword payload filtering.
