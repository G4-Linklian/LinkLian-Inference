from app.workers.post_summary_worker import PostSummaryWorker
from app.workers.qdrant_vector_store_worker import QdrantVectorStoreWorker
from app.workers.quiz_generation_worker import QuizGenerationWorker

REGISTRY: dict[str, type] = {
    PostSummaryWorker.queue_name: PostSummaryWorker,
    QdrantVectorStoreWorker.queue_name: QdrantVectorStoreWorker,
    QuizGenerationWorker.queue_name: QuizGenerationWorker,
}
