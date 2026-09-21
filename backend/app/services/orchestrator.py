import logging
import time
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from app.services.embedding_router import embedding_router
from app.services.retriever import qdrant_retriever
from app.services.mcp_client import github_mcp_client
from app.services.llm_router import llm_router
from app.services.tracer import tracer

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    query: str
    repository_id: str
    repository_name: str
    default_branch: str
    retrieved_chunks: List[Dict[str, Any]]
    needs_mcp: bool
    mcp_results: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    answer: str
    provider_used: str
    model_used: str
    fallback_occurred: bool
    fallback_chain: List[Dict[str, Any]]
    steps: List[Dict[str, Any]]


async def retrieve_step(state: GraphState) -> Dict[str, Any]:
    """Retrieve relevant code chunks from Qdrant vector database."""
    start_t = time.time()
    query = state["query"]
    repo_id = state.get("repository_id")

    query_vec, emb_provider = await embedding_router.embed_query(query)
    chunks = qdrant_retriever.search(
        query_vector=query_vec,
        repository_id=repo_id,
        limit=6,
        score_threshold=0.0
    )

    latency = int((time.time() - start_t) * 1000)
    step = {
        "name": "qdrant_retrieval",
        "status": "success",
        "latency_ms": latency,
        "details": {
            "embedding_provider": emb_provider,
            "chunks_found": len(chunks),
            "files": list({c.get("path") for c in chunks if c.get("path")})
        }
    }
    tracer.log_event("retrieval_complete", step["details"])
    return {
        "retrieved_chunks": chunks,
        "steps": state.get("steps", []) + [step]
    }


async def mcp_decision_step(state: GraphState) -> Dict[str, Any]:
    """Determine whether live repository inspection via GitHub MCP is required."""
    start_t = time.time()
    query = state["query"].lower()
    retrieved = state.get("retrieved_chunks", [])

    # Triggers for live MCP inspection:
    # 1. User asks explicitly for latest/current/live status
    # 2. No indexed chunks were found
    # 3. User specifically asks about pull requests, commits, or fresh updates
    live_keywords = ["latest", "recent", "live", "current", "head", "fresh", "commit", "prs", "issues"]
    needs_mcp = any(k in query for k in live_keywords) or len(retrieved) == 0

    latency = int((time.time() - start_t) * 1000)
    step = {
        "name": "mcp_decision",
        "status": "success",
        "latency_ms": latency,
        "details": {
            "needs_mcp": needs_mcp,
            "reason": "Live query keyword or empty vector match" if needs_mcp else "Indexed Qdrant context sufficient"
        }
    }
    return {
        "needs_mcp": needs_mcp,
        "steps": state.get("steps", []) + [step]
    }


def should_invoke_mcp(state: GraphState) -> str:
    return "mcp_fetch" if state.get("needs_mcp") else "llm_generate"


async def mcp_fetch_step(state: GraphState) -> Dict[str, Any]:
    """Execute live GitHub MCP tool calls when required."""
    start_t = time.time()
    repo_name = state.get("repository_name", "")
    query = state["query"]
    retrieved = state.get("retrieved_chunks", [])

    mcp_results = []
    # If we already have a top file path from retrieval, fetch current live content for accuracy
    if retrieved:
        top_file = retrieved[0].get("path")
        if top_file and repo_name:
            res = await github_mcp_client.get_file_contents(repo_name, top_file)
            mcp_results.append(res)
    else:
        # Otherwise execute GitHub code search
        if repo_name:
            res = await github_mcp_client.search_code(repo_name, query)
            mcp_results.append(res)

    latency = int((time.time() - start_t) * 1000)
    any_success = any(r.get("status") == "success" for r in mcp_results)
    step = {
        "name": "github_mcp_call",
        "status": "success" if any_success else "error",
        "latency_ms": latency,
        "details": {
            "tools_called": [r.get("tool") for r in mcp_results],
            "results_summary": [
                {"tool": r.get("tool"), "status": r.get("status"), "path": r.get("path")}
                for r in mcp_results
            ]
        }
    }
    tracer.log_event("mcp_execution_complete", step["details"])
    return {
        "mcp_results": mcp_results,
        "steps": state.get("steps", []) + [step]
    }


async def llm_generate_step(state: GraphState) -> Dict[str, Any]:
    """Synthesize final grounded answer using LLMRouter and assemble citations."""
    start_t = time.time()
    query = state["query"]
    chunks = state.get("retrieved_chunks", [])
    mcp_results = state.get("mcp_results", [])

    # Format context with strict file, line, and symbol references
    context_blocks = []
    sources = []

    for c in chunks:
        path = c.get("path", "")
        start_line = c.get("start_line", 1)
        end_line = c.get("end_line", 1)
        symbol = c.get("symbol")
        content = c.get("content", "")
        lang = c.get("language", "text")

        context_blocks.append(
            f"--- File: {path} (Lines {start_line}-{end_line}, Symbol: {symbol or 'None'}) ---\n"
            f"```{lang}\n{content}\n```"
        )
        sources.append({
            "path": path,
            "symbol": symbol,
            "start_line": start_line,
            "end_line": end_line,
            "source_type": "indexed",
            "language": lang,
            "snippet": content[:200] + "..." if len(content) > 200 else content
        })

    # Add live MCP context if retrieved
    for mr in mcp_results:
        if mr.get("status") == "success" and "content" in mr:
            path = mr.get("path", "")
            content = mr.get("content", "")
            context_blocks.append(
                f"--- Live File (via GitHub MCP): {path} ---\n{content[:1500]}"
            )
            sources.append({
                "path": path,
                "symbol": "live_file",
                "start_line": 1,
                "end_line": min(len(content.splitlines()), 60),
                "source_type": "live_mcp",
                "language": "text",
                "snippet": content[:200] + "..." if len(content) > 200 else content
            })

    system_prompt = (
        "You are RepoMind, an expert AI Codebase Intelligence Assistant. "
        "Answer the user's question accurately based strictly on the provided codebase context. "
        "Cite specific file paths, symbols, and line numbers when referencing code. "
        "If the information is not contained in the context, explicitly state what is missing."
    )

    combined_context = "\n\n".join(context_blocks)
    user_prompt = (
        f"Context from indexed repository:\n{combined_context}\n\n"
        f"User Question:\n{query}\n\n"
        "Provide a clear, direct, and well-structured answer citing file paths and symbols."
    )

    answer, provider_used, model_used, fallback_occurred, fallback_chain = await llm_router.generate_response(
        prompt=user_prompt,
        system_prompt=system_prompt,
        max_tokens=1500
    )

    latency = int((time.time() - start_t) * 1000)
    step = {
        "name": "llm_routing_generation",
        "status": "success",
        "latency_ms": latency,
        "details": {
            "provider_used": provider_used,
            "model_used": model_used,
            "fallback_occurred": fallback_occurred,
            "fallback_chain": fallback_chain
        }
    }
    tracer.log_event("generation_complete", step["details"])

    return {
        "answer": answer,
        "sources": sources,
        "provider_used": provider_used,
        "model_used": model_used,
        "fallback_occurred": fallback_occurred,
        "fallback_chain": fallback_chain,
        "steps": state.get("steps", []) + [step]
    }


def build_orchestrator_graph():
    builder = StateGraph(GraphState)

    builder.add_node("retrieve", retrieve_step)
    builder.add_node("mcp_decision", mcp_decision_step)
    builder.add_node("mcp_fetch", mcp_fetch_step)
    builder.add_node("llm_generate", llm_generate_step)

    builder.set_entry_point("retrieve")
    builder.add_edge("retrieve", "mcp_decision")
    builder.add_conditional_edges("mcp_decision", should_invoke_mcp, {
        "mcp_fetch": "mcp_fetch",
        "llm_generate": "llm_generate"
    })
    builder.add_edge("mcp_fetch", "llm_generate")
    builder.add_edge("llm_generate", END)

    return builder.compile()


orchestrator_graph = build_orchestrator_graph()
