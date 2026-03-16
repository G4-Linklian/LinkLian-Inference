from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.core.logger import AppLogger
from app.services.qdrant.client import get_qdrant_client
from app.services.qdrant.config import QdrantConfig
from app.services.qdrant.embedding import embed_text

from collections import Counter
import math

logger = AppLogger()


def retrieve_docs(
    q: str,
    post_id: str | int,
    limit: int = 10,
) -> list[dict]:
    query_vector = embed_text(q)
    
    logger.debug(
        "Qdrant retrieve docs",
        "QdrantRetrieve",
        {
            "post_id": post_id,
            "query": q,
            "limit": limit,
        },
    )

    client = get_qdrant_client()

    result = client.query_points(
        collection_name=QdrantConfig.COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="post_id",
                    match=MatchValue(value=int(post_id)),
                )
            ]
        ),
    )
    
    logger.debug(
        "Qdrant query successful",
        "QdrantRetrieve",
        {
            "length": len(result.points),
        }
    )

    return result


def get_top_pages(result):
    page_pairs = []
    page_count = None
    
    if (not result.points) or (not result.points[0].payload):
        return {
            "most_common_file": None,
            "most_common_page": None,
            "page_count": page_count,
            "k": 0,
            "top_k_pages": []
        }

    for point in result.points:
        payload = point.payload
        score = point.score
        
        if score < 0.3:  # Filter out points with low similarity score
            continue

        file_id = payload.get("file_count")
        file_name = payload.get("file_name")
        page_raw = payload.get("page")
        if page_raw is None:
            continue

        try:
            page = int(page_raw)
        except Exception:
            continue

        page_pairs.append((file_id, file_name, page))

        if page_count is None:
            page_count = payload.get("page_count")

    if not page_pairs:
        return {
            "most_common_file": None,
            "most_common_page": None,
            "page_count": page_count,
            "k": 0,
            "top_k_pages": [],
        }

    page_counter = Counter(page_pairs)

    most_common = page_counter.most_common(1)[0][0]

    most_common_file = most_common[0]
    most_common_page = most_common[1]

    safe_page_count = int(page_count) if page_count is not None else 1
    k = math.floor((safe_page_count / 7) * 2)
    if k == 0:
        k = 1

    top_k_pairs = page_counter.most_common(k)

    top_k_pages = [
        {
            "file": file_id,
            "page": page,
            "count": count,
            "file_name" : file_name
        }
        for (file_id, file_name, page), count in top_k_pairs
    ]

    return {
        "most_common_file": most_common_file,
        "most_common_page": most_common_page,
        "page_count": page_count,
        "k": k,
        "top_k_pages": top_k_pages
    }