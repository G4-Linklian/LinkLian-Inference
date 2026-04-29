from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.core.logger import AppLogger
from app.services.qdrant.client import get_qdrant_client
from app.services.qdrant.config import QdrantConfig
from app.services.qdrant.embedding import embed_text

from collections import Counter
import math

logger = AppLogger()
_POST_ID_INDEX_READY = False


def _is_missing_post_id_index_error(error_text: str) -> bool:
    return "Index required but not found" in error_text and '"post_id"' in error_text


def _is_not_found_error(error_text: str) -> bool:
    normalized = error_text.lower()
    return "404" in normalized and "not found" in normalized


def _extract_points(result) -> list:
    if isinstance(result, list):
        return result
    return getattr(result, "points", []) or []


def _ensure_post_id_index(client) -> None:
    global _POST_ID_INDEX_READY

    if _POST_ID_INDEX_READY:
        return

    try:
        # Qdrant Cloud can require a payload index before filtering by integer fields.
        client.create_payload_index(
            collection_name=QdrantConfig.COLLECTION_NAME,
            field_name="post_id",
            field_schema="integer",
        )
        logger.log(
            "Created payload index for post_id",
            "QdrantRetrieve",
            {"collection": QdrantConfig.COLLECTION_NAME},
        )
        _POST_ID_INDEX_READY = True
    except Exception as e:
        message = str(e).lower()
        if "already exists" in message:
            _POST_ID_INDEX_READY = True
            return

        logger.warn(
            "Failed to create payload index for post_id",
            "QdrantRetrieve",
            {"error": str(e)},
        )
        raise


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

    query_filter = Filter(
        must=[
            FieldCondition(
                key="post_id",
                match=MatchValue(value=int(post_id)),
            )
        ]
    )

    def _run_query_points():
        return client.query_points(
            collection_name=QdrantConfig.COLLECTION_NAME,
            query=query_vector,
            limit=limit,
            query_filter=query_filter,
        )

    def _run_search():
        # Fallback for servers that do not expose query_points endpoint.
        return client.search(
            collection_name=QdrantConfig.COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter,
        )

    try:
        result = _run_query_points()
    except Exception as e:
        error_text = str(e)
        if _is_missing_post_id_index_error(error_text):
            _ensure_post_id_index(client)
            result = _run_query_points()
        elif _is_not_found_error(error_text):
            logger.warn(
                "query_points endpoint returned 404, fallback to search",
                "QdrantRetrieve",
                {"collection": QdrantConfig.COLLECTION_NAME},
            )
            try:
                result = _run_search()
            except Exception as fallback_error:
                fallback_text = str(fallback_error)
                if _is_missing_post_id_index_error(fallback_text):
                    _ensure_post_id_index(client)
                    result = _run_search()
                else:
                    raise
        else:
            raise
    
    logger.debug(
        "Qdrant query successful",
        "QdrantRetrieve",
        {
            "length": len(_extract_points(result)),
        }
    )

    return result


def get_top_pages(result):
    points = _extract_points(result)
    page_pairs = []
    page_count = None
    
    if (not points) or (not points[0].payload):
        return {
            "most_common_file": None,
            "most_common_page": None,
            "page_count": page_count,
            "k": 0,
            "top_k_pages": []
        }

    for point in points:
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