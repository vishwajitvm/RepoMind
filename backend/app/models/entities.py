import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


def generate_uuid():
    return str(uuid.uuid4())


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(512), nullable=False, unique=True)
    default_branch = Column(String(100), default="main", nullable=False)
    status = Column(String(50), default="unindexed", nullable=False)  # unindexed, indexing, indexed, failed
    last_indexed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    indexing_jobs = relationship("IndexingJob", back_populates="repository", cascade="all, delete-orphan")
    files = relationship("IndexedFile", back_populates="repository", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="repository", cascade="all, delete-orphan")


class IndexingJob(Base):
    __tablename__ = "indexing_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    total_files = Column(Integer, default=0, nullable=False)
    indexed_files = Column(Integer, default=0, nullable=False)
    failed_files = Column(Integer, default=0, nullable=False)
    total_chunks = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    repository = relationship("Repository", back_populates="indexing_jobs")


class IndexedFile(Base):
    __tablename__ = "indexed_files"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    path = Column(String(1024), nullable=False, index=True)
    language = Column(String(50), default="unknown", nullable=False)
    size_bytes = Column(Integer, default=0, nullable=False)
    chunk_count = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="indexed", nullable=False)  # indexed, failed, skipped
    error_message = Column(Text, nullable=True)
    indexed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    repository = relationship("Repository", back_populates="files")


class ExecutionTrace(Base):
    __tablename__ = "execution_traces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), nullable=True, index=True)
    query = Column(Text, nullable=False)
    provider_used = Column(String(50), nullable=False)
    model_used = Column(String(100), nullable=False)
    fallback_occurred = Column(Boolean, default=False, nullable=False)
    fallback_chain = Column(JSON, default=list, nullable=False)
    mcp_invoked = Column(Boolean, default=False, nullable=False)
    mcp_tools_called = Column(JSON, default=list, nullable=False)
    retrieval_chunks_count = Column(Integer, default=0, nullable=False)
    latency_ms = Column(Integer, default=0, nullable=False)
    steps = Column(JSON, default=list, nullable=False)  # Array of execution steps for UI visualization
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), default="New Conversation", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    repository = relationship("Repository", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    sources = Column(JSON, default=list, nullable=False)  # Array of citations
    execution_id = Column(String(36), ForeignKey("execution_traces.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
