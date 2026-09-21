from datetime import datetime
from typing import List, Optional, Any, Dict, Literal
from pydantic import BaseModel, Field, ConfigDict


class RepositoryCreate(BaseModel):
    url: str = Field(..., description="GitHub repository URL or owner/repo format")
    name: Optional[str] = Field(None, description="Display name for the repository")
    default_branch: str = Field("main", description="Default branch to index")


class RepositoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    url: str
    default_branch: str
    status: str
    last_indexed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class IndexRequest(BaseModel):
    force_reindex: bool = Field(False, description="Re-index all files even if unchanged")


class IndexStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    repository_id: str
    status: str
    total_files: int
    indexed_files: int
    failed_files: int
    total_chunks: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class SourceCitation(BaseModel):
    path: str
    symbol: Optional[str] = None
    start_line: int
    end_line: int
    source_type: Literal["indexed", "live_mcp"] = "indexed"
    language: Optional[str] = None
    snippet: Optional[str] = None


class ExecutionStepItem(BaseModel):
    name: str
    status: Literal["pending", "running", "success", "error", "skipped"]
    latency_ms: int = 0
    details: Dict[str, Any] = Field(default_factory=dict)


class FallbackEvent(BaseModel):
    provider: str
    model: str
    status: Literal["failed", "success"]
    error: Optional[str] = None
    latency_ms: int = 0


class ExecutionTraceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    query: str
    provider_used: str
    model_used: str
    fallback_occurred: bool
    fallback_chain: List[FallbackEvent] = Field(default_factory=list)
    mcp_invoked: bool
    mcp_tools_called: List[str] = Field(default_factory=list)
    retrieval_chunks_count: int
    latency_ms: int
    steps: List[ExecutionStepItem] = Field(default_factory=list)
    created_at: datetime


class ChatRequest(BaseModel):
    repository_id: str
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    message_id: str
    conversation_id: str
    answer: str
    sources: List[SourceCitation] = Field(default_factory=list)
    execution_id: str
    trace: ExecutionTraceResponse
