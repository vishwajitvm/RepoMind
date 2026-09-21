# RepoMind — Development Workflow Guide

## 1. Overview (In Plain Language)

Developing on RepoMind is built to be fast, reliable, and painless. 

You don't need to install PostgreSQL, Redis, Qdrant, or Ollama directly onto your computer. Docker runs all of these services in isolated containers, while volume mounts allow you to edit code in your local editor (like VS Code or Cursor) and see changes immediately without restarting containers.

---

## 2. Developer Inner Loop Diagram

![Developer Inner Loop and Live Container Synchronization](https://mermaid.ink/svg/Zmxvd2NoYXJ0IFRECiAgICBEZXYoW0VuZ2luZWVyXSkgLS0+fEVkaXRzIGNvZGUgbG9jYWxseXwgTG9jYWxGaWxlc1tMb2NhbCBSZXBvc2l0b3J5XQogICAgTG9jYWxGaWxlcyAtLT58Vm9sdW1lIE1vdW50IDozMDAwfCBGcm9udGVuZENvbnRhaW5lcltyZXBvbWluZC1mcm9udGVuZCA6MzAwMCBWaXRlIEhNUl0KICAgIExvY2FsRmlsZXMgLS0+fFZvbHVtZSBNb3VudCA6NjAwNnwgU3Rvcnlib29rQ29udGFpbmVyW3JlcG9taW5kLXN0b3J5Ym9vayA6NjAwNl0KICAgIExvY2FsRmlsZXMgLS0+fFZvbHVtZSBNb3VudCA6ODAwMHwgQmFja2VuZENvbnRhaW5lcltyZXBvbWluZC1iYWNrZW5kIDo4MDAwIFV2aWNvcm5dCiAgICBMb2NhbEZpbGVzIC0tPnxWb2x1bWUgTW91bnR8IFdvcmtlckNvbnRhaW5lcltyZXBvbWluZC13b3JrZXIgSW5nZXN0aW9uXQogICAgCiAgICBEZXYgLS0+fFJ1bnMgdGVzdCBzdWl0ZXwgUHl0ZXN0W3B5dGVzdCBiYWNrZW5kL3Rlc3RzXQogICAgRGV2IC0tPnxSdW5zIFVJIGNoZWNrc3wgVHlwZWNoZWNrW25wbSBydW4gYnVpbGQgLyB0eXBlLWNoZWNrXQogICAgRGV2IC0tPnxSdW5zIGxpdmUgaW50ZWdyYXRpb258IERvY2tlclRlc3RbcHl0aG9uIGJhY2tlbmQvdGVzdHMvdGVzdF9saXZlX2RvY2tlci5weV0=)

```mermaid
flowchart TD
    Dev([Engineer]) -->|Edits code locally| LocalFiles[Local Repository]
    LocalFiles -->|Volume Mount :3000| FrontendContainer[repomind-frontend :3000 Vite HMR]
    LocalFiles -->|Volume Mount :6006| StorybookContainer[repomind-storybook :6006]
    LocalFiles -->|Volume Mount :8000| BackendContainer[repomind-backend :8000 Uvicorn]
    LocalFiles -->|Volume Mount| WorkerContainer[repomind-worker Ingestion]
    
    Dev -->|Runs test suite| Pytest[pytest backend/tests]
    Dev -->|Runs UI checks| Typecheck[npm run build / type-check]
    Dev -->|Runs live integration| DockerTest[python backend/tests/test_live_docker.py]
```

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
