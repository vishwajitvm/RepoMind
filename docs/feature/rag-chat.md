# Feature: LangGraph Codebase Orchestration

## Purpose
Orchestrates semantic vector search, conditional MCP inspection, LLM reasoning, and source citation extraction in a clean, stateful graph workflow.

## State Graph Workflow
1. `retrieve`: Queries Qdrant for semantic code chunk matches.
2. `mcp_decision`: Evaluates whether current/live GitHub data is required.
3. `mcp_fetch`: Conditionally calls GitHub MCP tools (`search_code` or `get_file_contents`).
4. `llm_generate`: Formats prompt with strict line and file headers, invokes `LLMRouter`, and returns answer with `SourceCitation` array.
