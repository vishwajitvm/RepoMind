import os
import tempfile
import pytest
from app.models.entities import Repository, IndexingJob
from app.services.indexer import repository_indexer
from app.services.retriever import qdrant_retriever


@pytest.mark.asyncio
async def test_indexer_local_directory(db_session):
    with tempfile.TemporaryDirectory(prefix="test_repo_") as tmp_dir:
        src_dir = os.path.join(tmp_dir, "src")
        os.makedirs(src_dir, exist_ok=True)

        py_file = os.path.join(src_dir, "calc.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def multiply(x, y):\n    return x * y\n")

        ts_file = os.path.join(src_dir, "types.ts")
        with open(ts_file, "w", encoding="utf-8") as f:
            f.write("export interface Config {\n    port: number;\n}\n")

        git_dir = os.path.join(tmp_dir, ".git")
        os.makedirs(git_dir, exist_ok=True)
        with open(os.path.join(git_dir, "config"), "w", encoding="utf-8") as f:
            f.write("dummy git config")

        repo = Repository(
            name="test/local-calc",
            url=tmp_dir,
            default_branch="main",
            status="unindexed"
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)

        job = IndexingJob(
            repository_id=repo.id,
            status="pending"
        )
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)

        res = await repository_indexer.index_repository(
            repository_id=repo.id,
            job_id=job.id,
            session=db_session
        )

        assert res["status"] == "completed"
        assert res["indexed_files"] == 2
        assert res["failed_files"] == 0
        assert res["total_chunks"] >= 2

        dummy_vec = [0.05] * qdrant_retriever.vector_size
        search_res = qdrant_retriever.search(
            query_vector=dummy_vec,
            repository_id=repo.id,
            limit=5
        )
        assert len(search_res) >= 1
        paths = [r["path"] for r in search_res]
        assert any("calc.py" in p for p in paths)
