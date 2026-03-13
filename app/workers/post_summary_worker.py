import time

from app.pipeline.post_summary.post_summary import post_summary_pipeline
from app.workers.base import BaseWorker


class PostSummaryWorker(BaseWorker):

    queue_name = "ai_summary_queue"

    # ── job processor ─────────────────────────────────────────────────────────

    async def process(self, job, job_token):
        start_time = time.perf_counter()

        data            = job.data
        post_content_id = data.get("post_content_id")
        title           = data.get("title", "")
        content         = data.get("content", "")
        file            = data.get("file", [])
        file_count      = data.get("file_count", 0)

        self.logger.log(
            "Received summary job",
            self.__class__.__name__,
            {"post_content_id": post_content_id, "file_count": file_count},
        )

        result = await post_summary_pipeline(
            post_content_id,
            title,
            content,
            file,
            file_count,
        )

        end_time   = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000

        self.logger.log(
            "Finished summary job",
            self.__class__.__name__,
            {"post_content_id": post_content_id, "elapsedMs": round(elapsed_ms, 4)},
        )

        return {
            "post_content_id": post_content_id,
            "result":          result,
            "elapsedMs": round(elapsed_ms, 4),
        }
