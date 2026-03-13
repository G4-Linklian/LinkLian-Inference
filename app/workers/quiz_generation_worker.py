import asyncio
import time

from app.pipeline.quiz.quiz_generation import quiz_generation_pipeline
from app.workers.base import BaseWorker


class QuizGenerationWorker(BaseWorker):
    queue_name = "quiz_generation_queue"

    async def process(self, job, job_token):
        start_time = time.perf_counter()

        data = job.data
        post_content_id = data.get("post_content_id")
        difficulty = data.get("difficulty", "medium")
        num_questions = data.get("num_questions", 5)

        self.logger.log(
            "Received quiz generation job",
            self.__class__.__name__,
            {
                "post_content_id": post_content_id,
                "difficulty": difficulty,
                "num_questions": num_questions,
            },
        )

        result = await asyncio.to_thread(
            quiz_generation_pipeline,
            post_content_id,
            difficulty,
            num_questions,
        )

        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000

        self.logger.log(
            "Finished quiz generation job",
            self.__class__.__name__,
            {"post_content_id": post_content_id, "elapsedMs": round(elapsed_ms, 4)},
        )

        return {
            "post_content_id": post_content_id,
            "result": result,
            "elapsedMs": round(elapsed_ms, 4),
        }
