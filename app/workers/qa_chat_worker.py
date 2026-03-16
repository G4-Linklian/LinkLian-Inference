import time

from app.pipeline.qa_chat.qa_chat import qa_chat_pipeline
from app.workers.base import BaseWorker


class QAChatWorker(BaseWorker):
    queue_name = "qa_chat_queue"

    async def process(self, job, job_token):
        start_time = time.perf_counter()

        data = job.data
        ai_chat_id = data.get("ai_chat_id")
        post_id = data.get("post_id", ai_chat_id)
        question = data.get("question", "")

        self.logger.log(
            "Received q&a chat job",
            self.__class__.__name__,
            {
                "ai_chat_id": ai_chat_id,
                "post_id": post_id,
                "question": question,
            },
        )

        result = await qa_chat_pipeline(question, ai_chat_id, post_id)

        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000

        self.logger.log(
            "Finished q&a chat job",
            self.__class__.__name__,
            {"ai_chat_id": ai_chat_id, "elapsedMs": round(elapsed_ms, 4)},
        )

        return {
            "ai_chat_id": ai_chat_id,
            "question": question,
            "result": result,
            "elapsedMs": round(elapsed_ms, 4),
        }
