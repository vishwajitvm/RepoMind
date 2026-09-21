import logging
import hashlib
import time
from typing import List, Optional, Tuple
import httpx
from app.config import settings
from app.services.tracer import tracer

logger = logging.getLogger(__name__)


class EmbeddingRouter:
    """
    EmbeddingRouter handles generating dense vector embeddings for text chunks.
    It manages provider selection, batching, timeouts, retries, and automatic fallbacks
    (Gemini -> Ollama -> Local Deterministic Dense Fallback).
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def _generate_local_deterministic_embedding(self, text: str) -> List[float]:
        """
        Deterministic, normalized dense vector generator for local fallback and test environments.
        Produces consistent 384-dimensional unit-norm vectors based on character n-grams and hashing.
        """
        vec = [0.0] * self.dimension
        if not text:
            return vec

        # Tokenize simply
        words = text.lower().split()
        for i, word in enumerate(words):
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            weight = 1.0 / (1.0 + (i % 10) * 0.1)
            vec[idx] += weight

        # Also encode 3-character ngrams for subword similarity
        for i in range(len(text) - 2):
            trigram = text[i:i+3]
            h = int(hashlib.md5(trigram.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            vec[idx] += 0.5

        # Normalize to unit sphere (L2 norm)
        norm = sum(x * x for x in vec) ** 0.5
        if norm > 0:
            vec = [round(x / norm, 6) for x in vec]
        return vec

    async def _embed_gemini(self, texts: List[str]) -> List[List[float]]:
        """Call Gemini text-embedding-004 API."""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_EMBEDDING_MODEL}:batchEmbedContents?key={settings.GEMINI_API_KEY}"
        requests_payload = [
            {"model": f"models/{settings.GEMINI_EMBEDDING_MODEL}", "content": {"parts": [{"text": t}]}}
            for t in texts
        ]

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json={"requests": requests_payload})
            resp.raise_for_status()
            data = resp.json()
            embeddings = []
            for item in data.get("embeddings", []):
                values = item.get("values", [])
                # Truncate or pad to expected dimension if needed
                if len(values) > self.dimension:
                    values = values[:self.dimension]
                elif len(values) < self.dimension:
                    values = values + [0.0] * (self.dimension - len(values))
                embeddings.append(values)
            return embeddings

    async def _embed_ollama(self, texts: List[str]) -> List[List[float]]:
        """Call Ollama embedding endpoint."""
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/embed"
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json={
                "model": settings.OLLAMA_EMBEDDING_MODEL,
                "input": texts
            })
            resp.raise_for_status()
            data = resp.json()
            embeddings = data.get("embeddings", [])
            adjusted = []
            for vec in embeddings:
                if len(vec) > self.dimension:
                    vec = vec[:self.dimension]
                elif len(vec) < self.dimension:
                    vec = vec + [0.0] * (self.dimension - len(vec))
                adjusted.append(vec)
            return adjusted

    async def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """Call OpenAI embeddings API."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")

        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "input": texts,
            "model": settings.OPENAI_EMBEDDING_MODEL,
            "dimensions": self.dimension
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("data", [])
            # Sort by index to maintain ordering
            items.sort(key=lambda x: x.get("index", 0))
            embeddings = []
            for item in items:
                vec = item.get("embedding", [])
                if len(vec) > self.dimension:
                    vec = vec[:self.dimension]
                elif len(vec) < self.dimension:
                    vec = vec + [0.0] * (self.dimension - len(vec))
                embeddings.append(vec)
            return embeddings

    async def embed_batch(self, texts: List[str]) -> Tuple[List[List[float]], str]:
        """
        Embed a list of text strings with bounded retries and automatic fallback.
        Returns (list_of_vectors, provider_used).
        """
        if not texts:
            return [], "none"

        # Determine priority based on configuration
        providers = []
        if settings.EMBEDDING_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            providers.append("gemini")
        elif settings.EMBEDDING_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            providers.append("openai")
        elif settings.EMBEDDING_PROVIDER == "ollama":
            providers.append("ollama")

        # Include fallbacks
        if "gemini" not in providers and settings.GEMINI_API_KEY:
            providers.append("gemini")
        if "openai" not in providers and settings.OPENAI_API_KEY:
            providers.append("openai")
        if "ollama" not in providers and settings.OLLAMA_BASE_URL:
            providers.append("ollama")
        providers.append("local")

        last_error = None
        for provider in providers:
            try:
                start_t = time.time()
                if provider == "gemini":
                    vecs = await self._embed_gemini(texts)
                elif provider == "openai":
                    vecs = await self._embed_openai(texts)
                elif provider == "ollama":
                    vecs = await self._embed_ollama(texts)
                else:
                    vecs = [self._generate_local_deterministic_embedding(t) for t in texts]

                latency_ms = int((time.time() - start_t) * 1000)
                logger.info(f"EmbeddingRouter: generated {len(texts)} embeddings via {provider} in {latency_ms}ms")
                tracer.log_event(
                    event_name="embedding_batch_completed",
                    message=f"Generated {len(texts)} embeddings via '{provider}' in {latency_ms}ms",
                    logger_name="embedding",
                    level="DEBUG",
                    provider=provider,
                    count=len(texts),
                    latency_ms=latency_ms
                )
                return vecs, provider
            except Exception as e:
                logger.warning(f"EmbeddingRouter: provider {provider} failed: {e}. Attempting fallback...")
                tracer.log_event(
                    event_name="embedding_provider_failed",
                    message=f"Embedding provider '{provider}' failed ({e}) — attempting fallback",
                    logger_name="embedding",
                    level="WARNING",
                    failed_provider=provider,
                    error=str(e)
                )
                last_error = e
                continue

        # Ultimate fallback
        vecs = [self._generate_local_deterministic_embedding(t) for t in texts]
        return vecs, "local"

    async def embed_query(self, query: str) -> Tuple[List[float], str]:
        """Convenience method to embed a single search query."""
        vecs, provider = await self.embed_batch([query])
        return vecs[0], provider


embedding_router = EmbeddingRouter(dimension=settings.QDRANT_VECTOR_SIZE)
