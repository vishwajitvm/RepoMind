import os
import shutil
import tempfile
import logging
import time
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import git
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.code_parser import CodeParser, is_ignored_file, detect_language
from app.services.embedding_router import embedding_router
from app.services.retriever import qdrant_retriever
from app.models.entities import Repository, IndexingJob, IndexedFile
from app.database import AsyncSessionLocal
from app.services.tracer import tracer

logger = logging.getLogger(__name__)


@asynccontextmanager
async def _get_session_scope(provided_session: Optional[AsyncSession] = None):
    if provided_session is not None:
        yield provided_session
    else:
        async with AsyncSessionLocal() as session:
            yield session


class RepositoryIndexer:
    """
    Handles robust, resumable repository indexing:
    1. Shallow clone or local path scanning
    2. File-level filtering (ignoring binaries, node_modules, .git, secrets)
    3. Code-aware semantic chunking
    4. Batch embedding generation via EmbeddingRouter
    5. Storage in Qdrant with detailed metadata
    6. Isolated file error boundaries (one bad file does not abort the job)
    """

    async def index_repository(
        self,
        repository_id: str,
        job_id: str,
        session: Optional[AsyncSession] = None,
        force_reindex: bool = False
    ) -> Dict[str, Any]:
        async with _get_session_scope(session) as s:
            repo_res = await s.execute(select(Repository).where(Repository.id == repository_id))
            repo = repo_res.scalar_one_or_none()
            if not repo:
                raise ValueError(f"Repository {repository_id} not found")

            job_res = await s.execute(select(IndexingJob).where(IndexingJob.id == job_id))
            job = job_res.scalar_one_or_none()
            if not job:
                raise ValueError(f"IndexingJob {job_id} not found")

            job.status = "processing"
            repo.status = "indexing"
            await s.commit()

        tracer.log_event(
            event_name="indexing_started",
            message=f"Repository indexing started for {repo.name} (branch: {repo.default_branch})",
            logger_name="indexer",
            level="INFO",
            repository_id=repository_id,
            job_id=job_id,
            url=repo.url
        )

        temp_dir = tempfile.mkdtemp(prefix="repomind_idx_")
        target_dir = temp_dir
        is_temp = True

        try:
            if os.path.isdir(repo.url):
                target_dir = repo.url
                is_temp = False
                logger.info(f"Indexing local directory: {target_dir}")
            else:
                logger.info(f"Cloning {repo.url} branch {repo.default_branch} into {temp_dir}...")
                git.Repo.clone_from(
                    repo.url,
                    temp_dir,
                    depth=1,
                    branch=repo.default_branch
                )

            discovered_files: List[str] = []
            for root, dirs, files in os.walk(target_dir):
                dirs[:] = [d for d in dirs if not is_ignored_file(os.path.join(root, d))]
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), target_dir).replace("\\", "/")
                    if not is_ignored_file(rel_path):
                        discovered_files.append(rel_path)

            tracer.log_event(
                event_name="repository_discovered",
                message=f"Discovered {len(discovered_files)} candidate source files in {repo.name}",
                logger_name="indexer",
                level="INFO",
                repository_id=repository_id,
                total_files=len(discovered_files)
            )

            async with _get_session_scope(session) as s:
                job_res = await s.execute(select(IndexingJob).where(IndexingJob.id == job_id))
                curr_job = job_res.scalar_one()
                curr_job.total_files = len(discovered_files)
                await s.commit()

            indexed_count = 0
            failed_count = 0
            total_chunks = 0

            for rel_path in discovered_files:
                full_path = os.path.join(target_dir, rel_path)
                try:
                    file_size = os.path.getsize(full_path)
                    if file_size > 1024 * 1024:
                        logger.info(f"Skipping large file ({file_size} bytes): {rel_path}")
                        tracer.log_event(
                            event_name="indexing_file_skipped",
                            message=f"Skipped large file ({file_size} bytes): {rel_path}",
                            logger_name="indexer",
                            level="WARNING",
                            repository_id=repository_id,
                            path=rel_path,
                            size_bytes=file_size
                        )
                        continue

                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()

                    chunks = CodeParser.chunk_file(rel_path, content)
                    if not chunks:
                        continue

                    chunk_texts = [c.content for c in chunks]
                    vectors, provider = await embedding_router.embed_batch(chunk_texts)

                    chunk_dicts = [c.to_dict() for c in chunks]
                    qdrant_retriever.upsert_chunks(
                        repository_id=repository_id,
                        repository_name=repo.name,
                        branch=repo.default_branch,
                        chunks=chunk_dicts,
                        vectors=vectors
                    )

                    tracer.log_event(
                        event_name="code_parse_completed",
                        message=f"Parsed and indexed {len(chunks)} chunks from {rel_path}",
                        logger_name="parser",
                        level="INFO",
                        repository_id=repository_id,
                        path=rel_path,
                        chunk_count=len(chunks),
                        provider=provider
                    )

                    indexed_count += 1
                    total_chunks += len(chunks)

                    async with _get_session_scope(session) as s:
                        file_record = IndexedFile(
                            repository_id=repository_id,
                            path=rel_path,
                            language=detect_language(rel_path),
                            size_bytes=file_size,
                            chunk_count=len(chunks),
                            status="indexed"
                        )
                        s.add(file_record)
                        await s.commit()

                except Exception as file_err:
                    logger.warning(f"Failed indexing file {rel_path}: {file_err}")
                    tracer.log_event(
                        event_name="indexing_file_failed",
                        message=f"Failed parsing {rel_path} — {file_err}",
                        logger_name="parser",
                        level="WARNING",
                        repository_id=repository_id,
                        path=rel_path,
                        error=str(file_err)
                    )
                    failed_count += 1
                    async with _get_session_scope(session) as s:
                        file_record = IndexedFile(
                            repository_id=repository_id,
                            path=rel_path,
                            language=detect_language(rel_path),
                            size_bytes=0,
                            chunk_count=0,
                            status="failed",
                            error_message=str(file_err)
                        )
                        s.add(file_record)
                        await s.commit()

            async with _get_session_scope(session) as s:
                job_res = await s.execute(select(IndexingJob).where(IndexingJob.id == job_id))
                curr_job = job_res.scalar_one()
                curr_job.status = "completed"
                curr_job.indexed_files = indexed_count
                curr_job.failed_files = failed_count
                curr_job.total_chunks = total_chunks
                curr_job.completed_at = job.started_at

                repo_res = await s.execute(select(Repository).where(Repository.id == repository_id))
                curr_repo = repo_res.scalar_one()
                curr_repo.status = "indexed"
                curr_repo.last_indexed_at = job.started_at

                await s.commit()

            tracer.log_event(
                event_name="indexing_completed",
                message=f"Repository indexing completed — {indexed_count} files, {total_chunks} chunks",
                logger_name="indexer",
                level="INFO",
                repository_id=repository_id,
                job_id=job_id,
                total_files=len(discovered_files),
                indexed_files=indexed_count,
                failed_files=failed_count,
                total_chunks=total_chunks
            )

            return {
                "status": "completed",
                "indexed_files": indexed_count,
                "failed_files": failed_count,
                "total_chunks": total_chunks
            }

        except Exception as e:
            logger.error(f"Fatal error during repository indexing: {e}")
            tracer.log_event(
                event_name="indexing_failed",
                message=f"Repository indexing failed: {e}",
                logger_name="indexer",
                level="ERROR",
                repository_id=repository_id,
                job_id=job_id,
                error=str(e)
            )
            async with _get_session_scope(session) as s:
                job_res = await s.execute(select(IndexingJob).where(IndexingJob.id == job_id))
                curr_job = job_res.scalar_one_or_none()
                if curr_job:
                    curr_job.status = "failed"
                    curr_job.error_message = str(e)

                repo_res = await s.execute(select(Repository).where(Repository.id == repository_id))
                curr_repo = repo_res.scalar_one_or_none()
                if curr_repo:
                    curr_repo.status = "failed"

                await s.commit()
            raise

        finally:
            if is_temp and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)


repository_indexer = RepositoryIndexer()
