from app.workers.post_summary_worker import PostSummaryWorker
from app.workers.qa_chat_worker import QAChatWorker
from app.workers.qdrant_vector_store_worker import QdrantVectorStoreWorker
from app.workers.quiz_generation_worker import QuizGenerationWorker

REGISTRY: dict[str, type] = {
    PostSummaryWorker.queue_name: PostSummaryWorker,
    QAChatWorker.queue_name: QAChatWorker,
    QdrantVectorStoreWorker.queue_name: QdrantVectorStoreWorker,
    QuizGenerationWorker.queue_name: QuizGenerationWorker,
}
