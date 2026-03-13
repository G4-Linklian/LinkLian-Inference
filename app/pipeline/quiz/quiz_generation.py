from app.core.file import safe_json_parse
from app.core.logger import AppLogger
from app.services.blob.blob_storage import upload_json_to_blob, upload_text_to_blob
from app.services.llm.quiz.quiz import quiz_generater
from app.core.file import load_text_from_url

logger = AppLogger()


def quiz_generation_pipeline(
    post_content_id: str,
    difficulty: str,
    num_questions: int,
) -> dict:
    try:
        logger.log(
            "Running quiz generation pipeline",
            "QuizGenerationPipeline",
            {
                "post_content_id": post_content_id,
                "difficulty": difficulty,
                "num_questions": num_questions,
            },
        )
        
        url_text = f"https://linklianstorage.blob.core.windows.net/ai-summary/summary-post-announcement/all-{post_content_id}.txt"
        summary_text = load_text_from_url(url_text)

        raw_quiz = quiz_generater(summary_text, difficulty, num_questions)
        quiz_parse = safe_json_parse(raw_quiz) or {}


        return quiz_parse
    
    
    except Exception as e:
        logger.error(
            "Quiz generation pipeline failed",
            "QuizGenerationPipeline",
            {
                "post_content_id": post_content_id,
                "error": str(e),
            },
        )
        return {
            "success": False,
            "message": str(e),
        }
