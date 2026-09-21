# RepoMind — Local Development Guide

## Prerequisites

- **Docker & Docker Compose** (Recommended runtime boundary)
- Optional host tools for offline test execution: Python 3.11+, Node.js 20+

---

## 1. Running with Docker Compose (Recommended)

Start the complete application stack (including Storybook):

```bash
docker compose up -d --build
```

This launches all 9 services:
- **Frontend SPA**: `http://localhost:3000`
- **Storybook UI**: `http://localhost:6006` (Component Library & Visual Workbench)
- **Backend API**: `http://localhost:8000` (Swagger docs at `/docs`)
- **PostgreSQL**: `localhost:5432`
- **Redis Queue**: `localhost:6379`
- **Qdrant Vector DB**: `http://localhost:6333` (Web UI at `http://localhost:6333/dashboard`)
- **Ollama**: `http://localhost:11434`
- **GitHub MCP Server**: `ghcr.io/github/github-mcp-server`
- **Background Worker**: Consumes ingestion jobs from Redis

---

## 2. Storybook Docker Service

Storybook runs as a first-class, dedicated Docker container (`repomind-storybook`) exposing port `6006`.

### Run Storybook Independently
You can start Storybook alone without starting the backend, databases, or AI services:

```bash
docker compose up -d storybook
```

### Rebuild Storybook Container
When adding new component stories or modifying styles:

```bash
docker compose build storybook
docker compose up -d storybook
```

### Inspect Storybook Logs
```bash
docker compose logs -f storybook
```

---

## 3. Backend Development & Testing

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

## 4. Frontend Local Development & Storybook (Host Mode)

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

Start Storybook on host:

```bash
cd frontend
npm run storybook
```

Build static Storybook bundle:

```bash
cd frontend
npm run build-storybook
```
