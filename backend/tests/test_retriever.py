import pytest
from app.services.retriever import QdrantRetriever


def test_qdrant_retriever_upsert_and_search():
    # Use isolated in-memory retriever for test
    retriever = QdrantRetriever(collection_name="test_code_chunks")

    chunks = [
        {
            "path": "auth.py",
            "language": "python",
            "symbol": "login",
            "chunk_type": "function",
            "start_line": 1,
            "end_line": 10,
            "content": "def login(user, pw): return verify(pw)"
        }
    ]
    # Synthetic vector
    vec = [0.1] * retriever.vector_size
    vectors = [vec]

    count = retriever.upsert_chunks(
        repository_id="repo-123",
        repository_name="test/repo",
        branch="main",
        chunks=chunks,
        vectors=vectors
    )
    assert count == 1

    # Search with matching repository_id
    results = retriever.search(
        query_vector=vec,
        repository_id="repo-123",
        limit=5
    )
    assert len(results) == 1
    assert results[0]["path"] == "auth.py"
    assert results[0]["symbol"] == "login"
    assert results[0]["repository_id"] == "repo-123"

    # Search with different repository_id
    other_results = retriever.search(
        query_vector=vec,
        repository_id="repo-999",
        limit=5
    )
    assert len(other_results) == 0
