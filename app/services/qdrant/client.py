from qdrant_client import QdrantClient

from .config import QdrantConfig

_QDRANT_CLIENT: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _QDRANT_CLIENT

    if _QDRANT_CLIENT is not None:
        return _QDRANT_CLIENT

    if not QdrantConfig.URL:
        raise ValueError("QDRANT_URL is required")
    if not QdrantConfig.COLLECTION_NAME:
        raise ValueError("QDRANT_COLLECTION is required")

    _QDRANT_CLIENT = QdrantClient(
        url=QdrantConfig.URL,
        api_key=QdrantConfig.API_KEY,
        timeout=60,
    )
    return _QDRANT_CLIENT


def close_qdrant_client() -> None:
    global _QDRANT_CLIENT

    if _QDRANT_CLIENT is not None:
        _QDRANT_CLIENT.close()
        _QDRANT_CLIENT = None
