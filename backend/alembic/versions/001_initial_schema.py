"""Initial RepoMind schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-21 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "repositories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("url", sa.String(512), nullable=False, unique=True),
        sa.Column("default_branch", sa.String(100), nullable=False, server_default="main"),
        sa.Column("status", sa.String(50), nullable=False, server_default="unindexed"),
        sa.Column("last_indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "indexing_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("repository_id", sa.String(36), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("total_files", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("indexed_files", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_files", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_chunks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "indexed_files",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("repository_id", sa.String(36), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("path", sa.String(1024), nullable=False, index=True),
        sa.Column("language", sa.String(50), nullable=False, server_default="unknown"),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="indexed"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "execution_traces",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), nullable=True, index=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("provider_used", sa.String(50), nullable=False),
        sa.Column("model_used", sa.String(100), nullable=False),
        sa.Column("fallback_occurred", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("fallback_chain", sa.JSON(), nullable=False),
        sa.Column("mcp_invoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("mcp_tools_called", sa.JSON(), nullable=False),
        sa.Column("retrieval_chunks_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("steps", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("repository_id", sa.String(36), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False, server_default="New Conversation"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sources", sa.JSON(), nullable=False),
        sa.Column("execution_id", sa.String(36), sa.ForeignKey("execution_traces.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("execution_traces")
    op.drop_table("indexed_files")
    op.drop_table("indexing_jobs")
    op.drop_table("repositories")
