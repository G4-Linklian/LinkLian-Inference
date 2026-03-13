import os


class QdrantConfig:
    URL = os.getenv("QDRANT_URL")
    API_KEY = os.getenv("QDRANT_API_KEY")
    COLLECTION_NAME = os.getenv("QDRANT_COLLECTION")
