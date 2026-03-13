import uuid

from qdrant_client.models import PointStruct

from app.core.logger import AppLogger
from app.services.qdrant.client import get_qdrant_client
from app.services.qdrant.config import QdrantConfig
from app.services.qdrant.embedding import embed_text

logger = AppLogger()


def _build_points(
    key_points: list[str],
    post_id: str | int,
    page: str | int | None = None,
    file_name: str | None = None,
) -> list[PointStruct]:
    points: list[PointStruct] = []
    for kp in key_points:
        if not kp:
            continue
        vector = embed_text(kp)
        payload = {
            "text": kp,
            "post_id": post_id,
        }
        if page is not None:
            payload["page"] = page
        if file_name:
            payload["file_name"] = file_name

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload,
            )
        )

    return points


def push_keypoints_sigle(
    key_points: list[str],
    post_id: str | int,
    page: int | None = None,
    file_name: str | None = None,
) -> dict:
    try:
        if not key_points:
            return {"success": True, "inserted": 0}

        client = get_qdrant_client()

        points = _build_points(
            key_points,
            post_id,
            page=page,
            file_name=file_name,
        )

        if not points:
            return {"success": True, "inserted": 0}

        client.upsert(
            collection_name=QdrantConfig.COLLECTION_NAME,
            points=points,
        )

        logger.log(
            "Upserted vectors to Qdrant",
            "QdrantStore",
            {"count": len(points), "post_id": post_id, "page": page},
        )

        return {"success": True, "inserted": len(points)}
    except Exception as e:
        logger.error(
            "Upsert vectors to Qdrant failed",
            "QdrantStore",
            {"post_id": post_id, "page": page, "error": str(e)},
        )
        return {"success": False, "inserted": 0, "error": str(e)}


def push_keypoints_multi(
    pages: dict,
    post_id: str | int,
    file_name: str | None = None,
    file_count: int | None = None,
) -> dict:
    try:
        if not pages:
            return {"success": True, "inserted": 0, "pages": 0}

        client = get_qdrant_client()

        points: list[PointStruct] = []
        pages_count = 0
        logger.debug(
            "Building points for multiple pages",
            "QdrantStore",
            {
                "post_id": post_id,
                "file_name": file_name,
            },
        )
        for page_key, key_points in pages.items():
            if not isinstance(key_points, list) or not key_points:
                continue
            page_points = _build_points(
                key_points,
                post_id,
                page=page_key,
                file_name=file_name,
                file_count=file_count,
            )
            if page_points:
                points.extend(page_points)
                pages_count += 1
                logger.debug(
                    "Built points for page",
                    "QdrantStore",
                    {
                        "post_id": post_id,
                        "file_name": file_name,
                        "page": page_key,
                        "key_points_count": len(key_points),
                        "points_built": len(page_points),
                        "file_count": file_count,
                    },
                )

        if not points:
            return {"success": True, "inserted": 0, "pages": 0}

        client.upsert(
            collection_name=QdrantConfig.COLLECTION_NAME,
            points=points,
        )

        logger.log(
            "Upserted vectors to Qdrant (multi)",
            "QdrantStore",
            {
                "count": len(points),
                "post_id": post_id,
                "file_name": file_name,
                "pages": pages_count,
            },
        )

        return {"success": True, "inserted": len(points), "pages": pages_count}
    except Exception as e:
        logger.error(
            "Upsert vectors to Qdrant (multi) failed",
            "QdrantStore",
            {"post_id": post_id, "file_name": file_name, "error": str(e), "file_count": file_count},
        )
        return {"success": False, "inserted": 0, "pages": 0, "error": str(e)}
