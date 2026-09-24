# RepoMind — Troubleshooting Guide

## 1. Overview (In Plain Language)

When developing or running a complex multi-container application, problems can occasionally occur: a service might take too long to start, a network port might be blocked, or an AI provider might be experiencing downtime.

This guide provides direct, step-by-step diagnostic procedures to quickly identify root causes and resolve issues without guesswork.

---

## 2. Interactive Troubleshooting Decision Tree

![RepoMind Troubleshooting Decision Tree](https://mermaid.ink/svg/Zmxvd2NoYXJ0IFRECiAgICBTdGFydChbRW5jb3VudGVyZWQgSXNzdWVdKSAtLT4gQ2hlY2tFbmRwb2ludHtXaGF0IGZhaWxlZD99CiAgICAKICAgIENoZWNrRW5kcG9pbnQgLS0+fEhUVFAgNDA0IG9uIC90cmFjZW5lc3R8IFNsYXNoRml4W0NoZWNrIFRyYWlsaW5nIFNsYXNoOiB2aXNpdCAvdHJhY2VuZXN0LyBpbnN0ZWFkXQogICAgQ2hlY2tFbmRwb2ludCAtLT58Q09SUyBFcnJvciBpbiBCcm93c2VyfCBDb3JzRml4W0NoZWNrIENPUlNfT1JJR0lOUyBpbiBiYWNrZW5kLy5lbnYgaW5jbHVkZXMgZnJvbnRlbmQgaG9zdF0KICAgIENoZWNrRW5kcG9pbnQgLS0+fFBvc3RncmVTUUwgQ29ubmVjdGlvbiBFcnJvcnwgRGJGaXhbQ2hlY2sgcmVwb21pbmQtcG9zdGdyZXMgaGVhbHRoOiBwZ19pc3JlYWR5XQogICAgQ2hlY2tFbmRwb2ludCAtLT58UWRyYW50IFNlYXJjaCBFbXB0eXwgUWRyYW50Rml4W1ZlcmlmeSBjb2xsZWN0aW9uIHJlcG9taW5kX2NvZGVfY2h1bmtzIGRpbWVuc2lvbiBpcyAzODRdCiAgICBDaGVja0VuZHBvaW50IC0tPnxPbGxhbWEgNDA0IE5vdCBGb3VuZHwgT2xsYW1hRml4W0V4ZWN1dGU6IGRvY2tlciBleGVjIC1pdCByZXBvbWluZC1vbGxhbWEgb2xsYW1hIHB1bGwgZGVlcHNlZWstcjE6MS41Yl0KICAgIENoZWNrRW5kcG9pbnQgLS0+fEdpdEh1YiBNQ1AgUmF0ZSBMaW1pdHwgTWNwRml4W1ZlcmlmeSBHSVRIVUJfUEVSU09OQUxfQUNDRVNTX1RPS0VOIGluIGJhY2tlbmQvLmVudl0=)

```mermaid
flowchart TD
    Start([Encountered Issue]) --> CheckEndpoint{What failed?}
    
    CheckEndpoint -->|HTTP 404 on /tracenest| SlashFix[Check Trailing Slash: visit /tracenest/ instead]
    CheckEndpoint -->|CORS Error in Browser| CorsFix[Check CORS_ORIGINS in backend/.env includes frontend host]
    CheckEndpoint -->|PostgreSQL Connection Error| DbFix[Check repomind-postgres health: pg_isready]
    CheckEndpoint -->|Qdrant Search Empty| QdrantFix[Verify collection repomind_code_chunks dimension is 384]
    CheckEndpoint -->|Ollama 404 Not Found| OllamaFix[Execute: docker exec -it repomind-ollama ollama pull deepseek-r1:1.5b]
    CheckEndpoint -->|GitHub MCP Rate Limit| McpFix[Verify GITHUB_PERSONAL_ACCESS_TOKEN in backend/.env]
```

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
