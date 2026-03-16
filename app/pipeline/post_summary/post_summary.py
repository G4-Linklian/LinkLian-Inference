from app.core.logger import AppLogger
from app.services.blob.blob_storage import upload_text_to_blob, upload_json_to_blob
from app.services.llm.summary.summary import summarize_all_page
from app.core.file import safe_json_parse
from app.pipeline.post_summary.pdf.pdf_summary import process_pdf_summary
from app.pipeline.post_summary.image.image_summary import process_image_summary
from bullmq import Queue
from app.workers.base import REDIS_CONN_OPTS
import os

logger = AppLogger()
QDRANT_STORE = os.getenv("QDRANT_STORE", "false").lower() == "true"

async def post_summary_pipeline(
    post_content_id: str,
    title: str,
    content: str,
    file: list[dict],
    file_count: int,
):
    queue = Queue("qdrant_vector_store", {"connection": REDIS_CONN_OPTS})
    try:
        logger.log(
            "Running post summary pipeline",
            "PostSummaryPipeline",
            {
                "post_content_id": post_content_id,
                "file_count": file_count,
                "title": title,
                "content": content,
                "file": file,
                "QDRANT_STORE": QDRANT_STORE,
            },
        )

        final_text_all_file = ""
        
        for i in range(file_count):

            logger.log(
                f"Processing file {i+1}/{file_count}",
                "PostSummaryPipeline",
                {
                    "file_index": i,
                    "file_info": file[i] if i < len(file) else None,
                },
            )

            if file[i]['file_type'] == 'pdf':
                result = process_pdf_summary(post_content_id, i, file[i])
                if not result.get("success"):
                    return result
                final_text_all_file += result.get("file_text", "")
                
                payload = {
                    "post_content_id": post_content_id,
                    "file_name": file[i].get("original_name", f"file_{i}"),
                    "page": result.get("page", {}),
                    "file_count" : i+1,
                    "page_count": result.get("page_count", 0),
                }
                
                if QDRANT_STORE:
                    await queue.add("qdrant-upsert-multi", payload)
                

            elif file[i]['file_type'] in {"png", "jpg", "jpeg"}:
                result = process_image_summary(post_content_id, i, file[i])
                if not result.get("success"):
                    return result
                final_text_all_file += result.get("file_text", "")
                
                payload = {
                    "post_content_id": post_content_id,
                    "file_name": file[i].get("original_name", f"file_{i}"),
                    "page": result.get("page", {}),
                    "file_count" : i+1,
                    "page_count": result.get("page_count", 0),
                }
                
                if QDRANT_STORE:
                    await queue.add("qdrant-upsert-multi", payload)
            else:

                logger.log(
                    f"Unknown file type",
                    "PostSummaryPipeline",
                    {
                        "file_type": file[i]['file_type'],
                    },
                )

                return {
                    "success": False,
                    "message": f"Unsupported file type: {file[i]['file_type']}"
                }

            logger.log(
                "Start Process All Page Summary",
                "PostSummaryPipeline",
            )

        summary_text = summarize_all_page(final_text_all_file, title, content)
            
        sap_parse = safe_json_parse(summary_text) or {}
            
        sap_blob_path = f"summary-post-announcement/all-{post_content_id}.json"
        sap_blob_url = upload_json_to_blob(
            container_name="ai-summary",
            blob_path=sap_blob_path,
            data=sap_parse,
        )
        logger.log(
            "Uploaded summary All JSON to blob",
            "PostSummaryPipeline",
            {"blob_url": sap_blob_url},
        )
            
        sap_blob_path = f"summary-post-announcement/all-{post_content_id}.txt"
        sap_blob_url = upload_text_to_blob(
            container_name="ai-summary",
            blob_path=sap_blob_path,
            text=final_text_all_file,
        )
        logger.log(
            "Uploaded summary All TXT to blob",
            "PostSummaryPipeline",
            {"blob_url": sap_blob_url},
        )

        return sap_parse

    except Exception as e:
        logger.error(
            "Post summary pipeline failed",
            "PostSummaryPipeline",
            {
                "post_content_id": post_content_id,
                "error": str(e),
            },
        )
        return {
            "success": False,
            "message": str(e),
        }
    finally:
        logger.log(
            "Closing queue connection",
            "PostSummaryPipeline",
        )
        await queue.close()
