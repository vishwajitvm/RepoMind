# RepoMind — Security Policy

RepoMind is an AI-powered codebase intelligence platform designed to index, retrieve, and reason about GitHub repositories using vector databases, language models, and Model Context Protocol (MCP) servers. Security, credential isolation, and source code privacy are core architectural priorities.

---

## 1. Supported Versions

Security updates and patches are actively maintained for the following versions:

| Version | Supported          | Status             |
|:--------|:-------------------|:-------------------|
| 0.1.x   | :white_check_mark: | Active Development |
| < 0.1.0 | :x:                | Unsupported        |

---

## 2. Reporting a Vulnerability

We take the security of RepoMind and the codebases it analyzes seriously. If you believe you have discovered a security vulnerability in RepoMind, please report it responsibly.

### 2.1 Contact Information
- **Email**: `security@repomind.dev` (or open a confidential GitHub Security Advisory via the repository's **Security** tab).
- **Subject**: `[SECURITY VULNERABILITY] <Component>: <Brief Description>`
- Please include:
  1. Description of the vulnerability and its potential impact.
  2. Step-by-step reproduction instructions (PoC script, curl command, or payload).
  3. Affected component (API, LangGraph orchestrator, Qdrant retriever, GitHub MCP client, TraceNest telemetry, frontend).
  4. Any proposed remediations or patches if available.

### 2.2 Response SLA
- **Initial Acknowledgment**: Within **48 hours** of report receipt.
- **Assessment & Triage**: Within **5 business days**, confirming reproduction and assigning a severity rating (CVSS v3.1).
- **Fix & Coordinated Disclosure**: We aim to release a patch within **14 to 30 days** depending on severity. We request that reporters adhere to coordinated disclosure guidelines and withhold public disclosure until a patched release is published.

---

## 3. Scope & Threat Model

### In Scope
- Remote code execution (RCE) via prompt injection or AST parsing vulnerabilities.
- Secret or API key exposure in TraceNest, LangSmith, or Docker logs.
- Privilege escalation or bypass of GitHub MCP read-only constraints.
- Unauthenticated access to Qdrant vector collections or PostgreSQL records.
- Server-Side Request Forgery (SSRF) via repository indexing URLs or MCP transport endpoints.
- Path traversal when resolving local repository workspaces or cached checkouts.

### Out of Scope
- Denial of Service (DoS) attacks on publicly exposed development endpoints without impact on data integrity.
- Vulnerabilities requiring physical access to an untrusted host running Docker.
- Outdated dependencies without a demonstrable attack path in RepoMind.
- Third-party LLM provider downtime, rate limits, or hallucinations not directly attributable to RepoMind's orchestration.

---

## 4. Key Security Boundaries & Guarantees

RepoMind implements strict architectural boundaries to safeguard user code and infrastructure:

1. **Strict Secret Redaction in Telemetry**:
   - All events emitted to TraceNest or LangSmith undergo automated regex masking for authentication headers, passwords, and API keys (`tracenest.security.redaction`).
   - Raw credentials are never persisted to disk or rendered in observability dashboards.

2. **Read-Only MCP Boundary**:
   - The GitHub MCP integration is constrained strictly to read-only capabilities (`search_code`, `get_file_contents`).
   - Code mutation, commit creation, branch modification, and administrative operations are forbidden.

3. **AST Filtering of Sensitive Files**:
   - Indexing strictly ignores `.env*`, `id_rsa`, `*.pem`, `*.key`, and secret-bearing credential files.
   - Code containing detected private keys or tokens is quarantined prior to embedding generation.

4. **Environment Isolation**:
   - Frontend and backend configurations are fully partitioned. Browser bundles never receive database passwords or AI provider keys.

---

## 5. Security Architecture Documentation

For complete technical specifications on data boundaries, secret scrubbing filters, and MCP sandboxing, see:
- [**Security Architecture Guide**](docs/security.md)
- [**Data Privacy Policy**](PRIVACY.md)
