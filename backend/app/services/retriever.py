import logging
import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.config import settings

logger = logging.getLogger(__name__)


class QdrantRetriever:
    """
    Manages vector storage and semantic retrieval in Qdrant.
    Preserves comprehensive code chunk metadata:
    repository_id, repository_name, branch, commit, path, language, symbol, chunk_type, start_line, end_line.
    """

    def __init__(self, collection_name: Optional[str] = None):
        self.collection_name = collection_name or settings.QDRANT_COLLECTION
        self.vector_size = settings.QDRANT_VECTOR_SIZE
        self.client = self._init_client()
        self._ensure_collection()

    def _init_client(self) -> QdrantClient:
        try:
            url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}"
            client = QdrantClient(
                url=url,
                api_key=settings.QDRANT_API_KEY,
                timeout=5.0,
                check_compatibility=False
            )
            client.get_collections()
            logger.info(f"Connected to remote Qdrant at {url}")
            return client
        except Exception as e:
            logger.warning(f"Could not connect to remote Qdrant ({e}). Initializing in-memory Qdrant instance for safe operation.")
            return QdrantClient(":memory:")

    def _ensure_collection(self) -> None:
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=self.vector_size,
                        distance=qmodels.Distance.COSINE
                    )
                )
                try:
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="repository_id",
                        field_schema=qmodels.PayloadSchemaType.KEYWORD
                    )
                except Exception:
                    pass
                logger.info(f"Created Qdrant collection '{self.collection_name}' with size {self.vector_size}")
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection: {e}")

    def upsert_chunks(
        self,
        repository_id: str,
        repository_name: str,
        branch: str,
        chunks: List[Dict[str, Any]],
        vectors: List[List[float]],
        commit: str = "HEAD"
    ) -> int:
        """
        Inserts or updates vector points in Qdrant with full code metadata.
        """
        if not chunks or not vectors:
            return 0

        points = []
        for chunk, vector in zip(chunks, vectors):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{repository_id}:{chunk['path']}:{chunk['start_line']}:{chunk.get('symbol', '')}"))
            payload = {
                "repository_id": repository_id,
                "repository_name": repository_name,
                "branch": branch,
                "commit": commit,
                "path": chunk["path"],
                "language": chunk.get("language", "unknown"),
                "symbol": chunk.get("symbol"),
                "chunk_type": chunk.get("chunk_type", "block"),
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
                "content": chunk["content"]
            }
            points.append(qmodels.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            ))

        batch_size = 64
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )

        logger.info(f"Upserted {len(points)} chunks into Qdrant for repository {repository_id}")
        return len(points)

    def search(
        self,
        query_vector: List[float],
        repository_id: Optional[str] = None,
        limit: int = 5,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the most semantically relevant code chunks from Qdrant.
        """
        filter_query = None
        if repository_id:
            filter_query = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="repository_id",
                        match=qmodels.MatchValue(value=repository_id)
                    )
                ]
            )

        if hasattr(self.client, "query_points"):
            res = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=filter_query,
                limit=limit,
                score_threshold=score_threshold
            )
            raw_hits = res.points
        else:
            raw_hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=filter_query,
                limit=limit,
                score_threshold=score_threshold
            )

        matches = []
        for hit in raw_hits:
            item = dict(hit.payload or {})
            item["score"] = hit.score
            matches.append(item)

        return matches

    def delete_by_repository(self, repository_id: str) -> None:
        """Deletes all chunks belonging to a specific repository."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="repository_id",
                        match=qmodels.MatchValue(value=repository_id)
                    )
                ]
            )
        )
        logger.info(f"Deleted vector points for repository {repository_id}")


qdrant_retriever = QdrantRetriever()
