import asyncio

from app.core.file import load_page_summary_detail, safe_json_parse
from app.core.logger import AppLogger
from app.services.llm.rewrite.rewrite import rewrite
from app.services.llm.qa.qa import qa
from app.services.qdrant.retrieve_docs import get_top_pages, retrieve_docs
from app.services.redis.ai_redis_service import AiRedisService

logger = AppLogger()


async def qa_chat_pipeline(
    question,
    ai_chat_id,
    post_id=None,
) -> str:
    logger.log(
        "Running q&a chat pipeline",
        "QAChatPipeline",
        {
            "question": question,
            "ai_chat_id": ai_chat_id,
        },
    )
    redis_service = AiRedisService()
    # target_post_id = post_id if post_id is not None else ai_chat_id

    summary_context = ""
    docs_text = ""
    chat_history = []

    try:
        # Chat History and Docs Overview are optional
        if ai_chat_id is not None:
            summary_context = await redis_service.get_docs_overview(ai_chat_id) or ""
            history_messages = await redis_service.get_chat_history(ai_chat_id)
            chat_history = [
                {"role": message["role"], "content": message["content"]}
                for message in history_messages
            ]

        # Rewriting question with context and history
        rewrite_result = await asyncio.to_thread(
            rewrite,
            question,
            summary_context,
            chat_history,
        )

        rewrite_parsed = safe_json_parse(rewrite_result) or {}

        logger.debug(
            "Rewrite result parsed",
            "QAChatPipeline",
            {
                "rewrite_parsed": rewrite_parsed,
            },
        )

        # Check Search from rewriting Agent

        final_search = ""
        search = False

        should_search = bool(rewrite_parsed.get("should_search", False))
        suggested_search_query = rewrite_parsed.get("suggested_search_query")
        rewritten_text = rewrite_parsed.get("rewritten_text", "")

        if (not should_search) and suggested_search_query:
            final_search = str(suggested_search_query)
            search = True
        elif should_search and rewritten_text:
            final_search = str(rewritten_text)
            search = True

        logger.debug(
            "search",
            "QAChatPipeline",
            {
                "final_search": final_search,
                "search": search,
            },
        )

        # Searching From Qdrant with key point

        if search and post_id is not None:
            point = await asyncio.to_thread(retrieve_docs, final_search, post_id, 20)
            info = get_top_pages(point)

            logger.debug(
                "Qdrant search result",
                "QAChatPipeline",
                {
                    "final_search": final_search,
                    "info": info,
                },
            )
            
            top_k_pages = info.get("top_k_pages", [])
            if top_k_pages:
                docs_text = load_page_summary_detail(post_id, top_k_pages)
            else:
                docs_text = ""
            
        logger.debug(
            "Loaded docs text from blob",
            "QAChatPipeline",
            {
                "docs_text": docs_text,
            },
        )

        raw_result = await asyncio.to_thread(
            qa,
            question,
            docs_text,
            chat_history,
        )
        parsed = safe_json_parse(raw_result) or {}
        answer = parsed.get("answer", "มีอะไรให้ช่วยไหม")

        # if ai_chat_id is not None:
        #     await redis_service.add_message(ai_chat_id, "user", str(question))
        #     await redis_service.add_message(ai_chat_id, "assistant", str(answer))

        return answer
    except Exception as e:
        logger.error(
            "q&a chat pipeline failed",
            "QAChatPipeline",
            {
                "ai_chat_id": ai_chat_id,
                "error": str(e),
            },
        )
        return "มีอะไรให้ช่วยไหม"
    finally:
        await redis_service.close()
