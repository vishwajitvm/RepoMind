# Feature: Official GitHub MCP Integration

## Purpose
Integrates the official containerized GitHub MCP server (`ghcr.io/github/github-mcp-server`) to inspect live repository source code when indexed vectors are insufficient or stale.

## Read-Only Tools Supported
- `search_code`: Queries code across the repository for specific keywords or symbols.
- `get_file_contents`: Fetches live, current file content and metadata for a specific path and git ref.

## Reliability & Fallback
- If the containerized MCP process is unreachable, the client falls back to the verified GitHub REST API if a token is present.
- If unauthenticated, the client logs the exact failure condition and relies on indexed vectors without fabricating results.
