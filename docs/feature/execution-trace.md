# Feature: Execution Trace & Telemetry

## Purpose
Exposes complete transparency to developers regarding model execution, latency, tool calls, and provider fallbacks for every question answered by the AI assistant.

## Telemetry Captured
- `query`: User's original prompt
- `provider_used` & `model_used`: Actual final LLM provider and model
- `fallback_occurred` & `fallback_chain`: Ordered list of attempted providers with errors and latencies
- `mcp_invoked` & `mcp_tools_called`: Exact MCP tool calls made
- `retrieval_chunks_count`: Number of Qdrant chunks supplied to context
- `steps`: Timeline of each LangGraph pipeline step with latency and metadata
- `latency_ms`: Total execution time
