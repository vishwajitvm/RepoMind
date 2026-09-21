# Contributing to RepoMind

Thank you for your interest in contributing to **RepoMind**! RepoMind is a small, professional, production-style proof of concept (POC) for AI codebase intelligence powered by React, TypeScript, FastAPI, PostgreSQL, Qdrant, LangGraph, and GitHub MCP.

We welcome contributions from the community. Please review this guide to understand our architectural standards, development workflow, and pull request procedures.

---

## 1. Code of Conduct

All contributors are expected to uphold our [**Code of Conduct**](CODE_OF_CONDUCT.md). Please read it before participating in our issues, discussions, or pull requests.

---

## 2. Core Architectural Philosophy

Contributors must adhere to the engineering rules outlined in `AGENTS.md`:

1. **Understand $\rightarrow$ Inspect $\rightarrow$ Implement $\rightarrow$ Verify $\rightarrow$ Document $\rightarrow$ Finish**:
   - Inspect existing abstractions before making changes.
   - Reuse existing utilities, components, and services instead of creating duplicates.
2. **Zero Hallucinations**:
   - Never invent external APIs, SDK methods, MCP tools, model identifiers, or configuration flags. Always verify against official documentation or installed package source.
3. **No Fake / Fabricated Functionality**:
   - Every feature must be genuinely wired and executable. Never hardcode mock results to make the POC appear functional.
4. **Token & Resource Efficiency**:
   - Never send entire repositories to an LLM. Leverage code-aware AST chunking, Qdrant semantic retrieval, and live MCP tools for targeted grounding.
5. **Docker-First Environment**:
   - All runtime services run inside Docker. Host-level installations of Python, Node, PostgreSQL, or Qdrant must not be required.

---

## 3. Development Setup

### 3.1 Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/)
- [Git](https://git-scm.com/)

### 3.2 Starting the Environment
Clone the repository and spin up all 9 containerized services:

```bash
# Clone the repository
git clone https://github.com/vishwajitvm/RepoMind.git
cd RepoMind

# Configure environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Launch the full Docker Compose stack
docker compose up -d --build
```

### 3.3 Active Services & Ports

| Service | Port | Description |
|:---|:---|:---|
| **Frontend Application** | `http://localhost:3000` | React 18 + Vite + Tailwind UI |
| **Storybook UI Catalog** | `http://localhost:6006` | Interactive component library |
| **Backend REST API** | `http://localhost:8000` | FastAPI server & OpenAPI docs (`/docs`) |
| **TraceNest Dashboard** | `http://localhost:8000/tracenest` | Application observability & execution traces |
| **Qdrant Vector DB** | `http://localhost:6333` | Vector collection & semantic retrieval engine |
| **PostgreSQL** | `localhost:5432` | Relational storage for repositories & jobs |
| **Redis** | `localhost:6379` | Background task queue & worker state |
| **Ollama Local LLM** | `http://localhost:11434` | Local model inference daemon |

---

## 4. Coding Standards

### 4.1 Frontend (React & TypeScript)
- **Strict TypeScript**: Avoid `any`; use strict typing and type narrowing (`unknown`). Never suppress compiler errors with `// @ts-ignore` or `// @ts-nocheck`.
- **Component Architecture**: Reusable, typed, accessible, and composable. Avoid giant multi-hundred-line components.
- **Storybook First**: Any new or updated reusable UI component must have a corresponding Storybook story under `frontend/src/stories/` demonstrating all interactive states (idle, loading, error, success).
- **Styling**: Tailwind CSS exclusively. Avoid arbitrary inline styles or custom unmanaged CSS files.
- **Server State**: Use TanStack Query (`@tanstack/react-query`) for server interactions and React Hook Form + Zod for form validation.

### 4.2 Backend (Python & FastAPI)
- **Type Hints**: All functions and methods must include explicit type annotations.
- **Data Modeling**: Use Pydantic v2 request/response schemas. Never accept or return untyped arbitrary dictionaries at API boundaries.
- **Database Migrations**: Relational schema modifications must be accompanied by an Alembic migration (`backend/alembic/versions/`).
- **Telemetry**: Emit structured, human-readable TraceNest events using `app.services.tracer.tracer` with appropriate component loggers (`api`, `chat`, `indexer`, `llm`, `mcp`, `retrieval`, `qdrant`).
- **Secret Redaction**: Never log passwords, API keys, or raw bearer tokens.

---

## 5. Verification & Testing

Before submitting a Pull Request, verify that your changes pass all automated tests and quality checks:

```bash
# 1. Run backend unit tests inside Docker
docker exec repomind-backend pytest tests -v

# 2. Run end-to-end live Docker integration pipeline
python backend/tests/test_live_docker.py

# 3. Verify documentation Mermaid diagrams
python scripts/audit_docs.py
```

If you modified frontend components:
```bash
# In the frontend directory or inside the frontend container
cd frontend
npm run build
npm run lint
```

---

## 6. Pull Request Guidelines

1. **Branch Naming**:
   - `feat/<feature-name>`: New feature or capability.
   - `fix/<bug-name>`: Bug fix or regression patch.
   - `docs/<topic>`: Documentation updates or additions.
   - `refactor/<scope>`: Code refactoring without behavioral changes.

2. **Commit Messages**:
   - Use clear, descriptive commit messages adhering to Conventional Commits:
     - `feat(indexer): add support for rust and go ast chunking`
     - `fix(retriever): handle qdrant connection retry on startup`
     - `docs(observability): update tracenest telemetry taxonomy`

3. **Submitting the PR**:
   - Fill out the provided [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md).
   - Link all relevant issues.
   - Ensure all CI checks and tests pass.

---

## 7. Reporting Issues & Requesting Features

- **Bug Reports**: Use our [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.yml) and include reproduction steps, environment details, and relevant TraceNest logs.
- **Feature Requests**: Use our [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.yml) detailing the use case, proposed solution, and architectural impact.
- **Security Vulnerabilities**: Do **not** open public issues for security vulnerabilities. Follow our [Security Policy](SECURITY.md).
