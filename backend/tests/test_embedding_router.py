import pytest
from app.services.embedding_router import embedding_router


@pytest.mark.asyncio
async def test_embed_batch_fallback():
    texts = [
        "def authenticate_user(token): return True",
        "class CodeIndexer: pass"
    ]
    vectors, provider = await embedding_router.embed_batch(texts)
    assert len(vectors) == 2
    assert len(vectors[0]) == embedding_router.dimension
    assert provider in ("local", "gemini", "ollama")

    # Verify vector normalization (norm should be ~1.0)
    norm = sum(x * x for x in vectors[0]) ** 0.5
    assert abs(norm - 1.0) < 0.05


@pytest.mark.asyncio
async def test_embed_query():
    vec, provider = await embedding_router.embed_query("how does authentication work?")
    assert len(vec) == embedding_router.dimension
    assert provider in ("local", "gemini", "ollama")
