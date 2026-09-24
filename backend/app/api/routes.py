import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.entities import Repository, IndexingJob, ExecutionTrace, Conversation, Message
from app.schemas.api_schemas import (
    RepositoryCreate,
    RepositoryResponse,
    IndexRequest,
    IndexStatusResponse,
    ChatRequest,
    ChatResponse,
    ExecutionTraceResponse,
    ExecutionStepItem,
    FallbackEvent,
    SourceCitation
)
from app.services.orchestrator import orchestrator_graph
from app.services.worker import dispatch_indexing_job
from app.services.tracer import tracer

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/repositories", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def create_repository(
    payload: RepositoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a GitHub repository for intelligence indexing."""
    # Check if repository already exists by URL
    clean_url = payload.url.strip()
    result = await db.execute(select(Repository).where(Repository.url == clean_url))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    repo_name = payload.name
    if not repo_name:
        parts = clean_url.rstrip("/").split("/")
        repo_name = f"{parts[-2]}/{parts[-1]}" if len(parts) >= 2 else parts[-1]

    repo = Repository(
        name=repo_name,
        url=clean_url,
        default_branch=payload.default_branch,
        status="unindexed"
    )
    db.add(repo)
    await db.commit()
    await db.refresh(repo)

    tracer.log_event(
        event_name="repository_registered",
        message=f"Repository registered successfully: {repo.name}",
        logger_name="repository",
        level="INFO",
        repository_id=repo.id,
        name=repo.name,
        url=repo.url
    )

    return repo


@router.get("/repositories", response_model=List[RepositoryResponse])
async def list_repositories(db: AsyncSession = Depends(get_db)):
    """List all registered repositories."""
    result = await db.execute(select(Repository).order_by(desc(Repository.created_at)))
    return result.scalars().all()


@router.get("/repositories/{repo_id}", response_model=RepositoryResponse)
async def get_repository(repo_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch details of a specific repository."""
    result = await db.execute(select(Repository).where(Repository.id == repo_id))
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo


@router.post("/repositories/{repo_id}/index", response_model=IndexStatusResponse)
async def trigger_indexing(
    repo_id: str,
    payload: IndexRequest,
    db: AsyncSession = Depends(get_db)
):
    """Trigger background indexing job for repository."""
    result = await db.execute(select(Repository).where(Repository.id == repo_id))
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    job = IndexingJob(
        repository_id=repo.id,
        status="pending"
    )
    db.add(job)
    repo.status = "indexing"
    await db.commit()
    await db.refresh(job)

    # Enqueue job to background worker
    await dispatch_indexing_job(repository_id=repo.id, job_id=job.id)

    tracer.log_event(
        event_name="indexing_queued",
        message=f"Repository indexing job queued for {repo.name}",
        logger_name="indexer",
        level="INFO",
        repository_id=repo.id,
        job_id=job.id
    )

    return IndexStatusResponse(
        repository_id=repo.id,
        status=job.status,
        total_files=job.total_files,
        indexed_files=job.indexed_files,
        failed_files=job.failed_files,
        total_chunks=job.total_chunks,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at
    )


@router.get("/repositories/{repo_id}/status", response_model=IndexStatusResponse)
async def get_indexing_status(repo_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve indexing status and metrics for a repository."""
    result = await db.execute(
        select(IndexingJob)
        .where(IndexingJob.repository_id == repo_id)
        .order_by(desc(IndexingJob.started_at))
        .limit(1)
    )
    latest_job = result.scalars().first()
    if not latest_job:
        # Check if repo exists
        repo_res = await db.execute(select(Repository).where(Repository.id == repo_id))
        repo = repo_res.scalar_one_or_none()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        return IndexStatusResponse(
            repository_id=repo.id,
            status=repo.status,
            total_files=0,
            indexed_files=0,
            failed_files=0,
            total_chunks=0
        )

    return IndexStatusResponse(
        repository_id=repo_id,
        status=latest_job.status,
        total_files=latest_job.total_files,
        indexed_files=latest_job.indexed_files,
        failed_files=latest_job.failed_files,
        total_chunks=latest_job.total_chunks,
        error_message=latest_job.error_message,
        started_at=latest_job.started_at,
        completed_at=latest_job.completed_at
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_codebase(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Execute LangGraph codebase question-answering with vector retrieval, MCP, and LLM fallback routing."""
    # Verify repository
    repo_res = await db.execute(select(Repository).where(Repository.id == payload.repository_id))
    repo = repo_res.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Get or create conversation
    conv_id = payload.conversation_id
    if conv_id:
        conv_res = await db.execute(select(Conversation).where(Conversation.id == conv_id))
        conversation = conv_res.scalar_one_or_none()
    else:
        conversation = None

    if not conversation:
        conversation = Conversation(
            repository_id=repo.id,
            title=payload.message[:40] + ("..." if len(payload.message) > 40 else "")
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=payload.message,
        sources=[]
    )
    db.add(user_msg)
    await db.commit()

    tracer.log_event(
        event_name="chat_started",
        message=f"Chat query received for repository: {repo.name}",
        logger_name="api",
        level="INFO",
        query=payload.message,
        repository_id=repo.id,
        conversation_id=conversation.id
    )

    # Invoke LangGraph orchestrator
    initial_state = {
        "query": payload.message,
        "repository_id": repo.id,
        "repository_name": repo.name,
        "default_branch": repo.default_branch,
        "retrieved_chunks": [],
        "needs_mcp": False,
        "mcp_results": [],
        "sources": [],
        "answer": "",
        "provider_used": "",
        "model_used": "",
        "fallback_occurred": False,
        "fallback_chain": [],
        "steps": []
    }

    graph_out = await orchestrator_graph.ainvoke(initial_state)

    # Compute total latency
    total_latency = sum(s.get("latency_ms", 0) for s in graph_out.get("steps", []))
    mcp_tools = [
        s["name"] for s in graph_out.get("steps", [])
        if "mcp" in s["name"].lower() and s["name"] != "mcp_decision"
    ]

    # Save ExecutionTrace to database
    trace = ExecutionTrace(
        conversation_id=conversation.id,
        query=payload.message,
        provider_used=graph_out.get("provider_used", "unknown"),
        model_used=graph_out.get("model_used", "unknown"),
        fallback_occurred=graph_out.get("fallback_occurred", False),
        fallback_chain=graph_out.get("fallback_chain", []),
        mcp_invoked=graph_out.get("needs_mcp", False),
        mcp_tools_called=mcp_tools,
        retrieval_chunks_count=len(graph_out.get("retrieved_chunks", [])),
        latency_ms=total_latency,
        steps=graph_out.get("steps", [])
    )
    db.add(trace)
    await db.commit()
    await db.refresh(trace)

    # Save assistant message
    asst_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=graph_out.get("answer", ""),
        sources=graph_out.get("sources", []),
        execution_id=trace.id
    )
    db.add(asst_msg)
    await db.commit()
    await db.refresh(asst_msg)

    tracer.log_event(
        event_name="chat_completed",
        message=f"Chat response completed — {len(asst_msg.sources)} sources cited ({trace.provider_used})",
        logger_name="chat",
        level="INFO",
        trace_id=trace.id,
        message_id=asst_msg.id,
        execution_id=trace.id,
        conversation_id=conversation.id,
        provider_used=trace.provider_used,
        model_used=trace.model_used,
        latency_ms=trace.latency_ms,
        sources_count=len(asst_msg.sources)
    )

    # Format trace response
    trace_resp = ExecutionTraceResponse(
        id=trace.id,
        query=trace.query,
        provider_used=trace.provider_used,
        model_used=trace.model_used,
        fallback_occurred=trace.fallback_occurred,
        fallback_chain=[FallbackEvent(**fb) for fb in trace.fallback_chain],
        mcp_invoked=trace.mcp_invoked,
        mcp_tools_called=trace.mcp_tools_called,
        retrieval_chunks_count=trace.retrieval_chunks_count,
        latency_ms=trace.latency_ms,
        steps=[ExecutionStepItem(**st) for st in trace.steps],
        created_at=trace.created_at
    )

    return ChatResponse(
        message_id=asst_msg.id,
        conversation_id=conversation.id,
        answer=asst_msg.content,
        sources=[SourceCitation(**s) for s in asst_msg.sources],
        execution_id=trace.id,
        trace=trace_resp
    )


@router.get("/executions/{execution_id}", response_model=ExecutionTraceResponse)
async def get_execution_trace(execution_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch complete telemetry execution trace for an AI response."""
    result = await db.execute(select(ExecutionTrace).where(ExecutionTrace.id == execution_id))
    trace = result.scalar_one_or_none()
    if not trace:
        raise HTTPException(status_code=404, detail="Execution trace not found")

    tracer.log_event(
        event_name="trace_completed",
        message=f"Execution trace retrieved for ID {execution_id[:8]}...",
        logger_name="observability",
        level="DEBUG",
        execution_id=execution_id,
        provider_used=trace.provider_used,
        latency_ms=trace.latency_ms
    )

    return ExecutionTraceResponse(
        id=trace.id,
        query=trace.query,
        provider_used=trace.provider_used,
        model_used=trace.model_used,
        fallback_occurred=trace.fallback_occurred,
        fallback_chain=[FallbackEvent(**fb) for fb in trace.fallback_chain],
        mcp_invoked=trace.mcp_invoked,
        mcp_tools_called=trace.mcp_tools_called,
        retrieval_chunks_count=trace.retrieval_chunks_count,
        latency_ms=trace.latency_ms,
        steps=[ExecutionStepItem(**st) for st in trace.steps],
        created_at=trace.created_at
    )
