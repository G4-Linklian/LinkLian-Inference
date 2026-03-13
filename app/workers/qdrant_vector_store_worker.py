import asyncio
import time

from app.pipeline.qdrant_store.qdrant_store import push_keypoints_multi
from app.workers.base import BaseWorker


class QdrantVectorStoreWorker(BaseWorker):
    queue_name = "qdrant_vector_store"

    async def process(self, job, job_token):
        start_time = time.perf_counter()

        data = job.data
        post_content_id = data.get("post_content_id")
        file_name = data.get("file_name")
        pages = data.get("page", {})
        file_count = data.get("file_count", 1)
        total_count = 0
        if isinstance(pages, dict):
            total_count = sum(
                len(key_points)
                for key_points in pages.values()
                if isinstance(key_points, list)
            )

        self.logger.log(
            "Received qdrant vector store job",
            self.__class__.__name__,
            {
                "post_content_id": post_content_id,
                "file_name": file_name,
                "count": total_count,
                "pages": list(pages.keys()) if isinstance(pages, dict) else None,
                "file_count": file_count,
            },
        )

        result = await asyncio.to_thread(
            push_keypoints_multi,
            pages,
            post_content_id,
            file_name,
            file_count,
        )

        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000

        self.logger.log(
            "Finished qdrant vector store job",
            self.__class__.__name__,
            {"post_content_id": post_content_id, "elapsedMs": round(elapsed_ms, 4), "file_count": file_count},
        )

        return {
            "post_content_id": post_content_id,
            "file_name": file_name,
            "result": result,
            "elapsedMs": round(elapsed_ms, 4),
        }
