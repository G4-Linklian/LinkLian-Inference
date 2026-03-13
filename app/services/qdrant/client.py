from qdrant_client import QdrantClient

from .config import QdrantConfig


def get_qdrant_client() -> QdrantClient:
    if not QdrantConfig.URL:
        raise ValueError("QDRANT_URL is required")
    if not QdrantConfig.COLLECTION_NAME:
        raise ValueError("QDRANT_COLLECTION is required")
    return QdrantClient(
        url=QdrantConfig.URL,
        api_key=QdrantConfig.API_KEY,
        timeout=60,
    )
