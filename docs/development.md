# RepoMind — Local Development Guide

## Prerequisites

- **Docker & Docker Compose** (Recommended runtime boundary)
- Optional host tools for offline test execution: Python 3.11+, Node.js 20+

---

## 1. Running with Docker Compose (Recommended)

Start the complete application stack:

```bash
docker compose up --build
```

This launches:
- **Frontend SPA**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000` (Swagger docs at `/docs`)
- **PostgreSQL**: `localhost:5432`
- **Redis Queue**: `localhost:6379`
- **Qdrant Vector DB**: `http://localhost:6333` (Web UI at `http://localhost:6333/dashboard`)
- **Ollama**: `http://localhost:11434`
- **GitHub MCP Server**: `ghcr.io/github/github-mcp-server`

---

## 2. Backend Development & Testing

Run tests on the host:

```bash
cd backend
python -m pytest tests -v
```

Apply database migrations:

```bash
cd backend
alembic upgrade head
```

Run background worker:

```bash
cd backend
python -m app.services.worker
```

---

## 3. Frontend Development & Storybook

Start Vite development server:

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Run TypeScript verification:

```bash
cd frontend
npx tsc --noEmit
```

Start Storybook component workbench:

```bash
cd frontend
npm run storybook
```
