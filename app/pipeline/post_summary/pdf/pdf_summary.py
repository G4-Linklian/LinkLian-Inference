from pdf2image import convert_from_bytes

from app.core.file import load_pdf_from_url, safe_json_parse, json_all_page
from app.core.logger import AppLogger
from app.services.blob.blob_storage import upload_json_to_blob
from app.services.llm.summary.summary import summarize_each_page

logger = AppLogger()


def process_pdf_summary(post_content_id: str, file_index: int, file_info: dict) -> dict:
    logger.log(
        "Processing PDF type",
        "PostSummaryPipeline",
    )

    azure_path = file_info.get("file_url")

    logger.log(
        "real azure_path",
        "PostSummaryPipeline",
        {
            "azure_path": azure_path,
        },
    )

    # azure_path = "https://linklianstorage.blob.core.windows.net/social-feed/fileattachment/260304_IntroToBioinformatics_HandsOn.pdf"

    pdf_bytes = load_pdf_from_url(azure_path)

    image_buffers = convert_from_bytes(pdf_bytes, dpi=50)

    logger.log(
        "Load Data From Blob and Converted PDF to images",
        "PostSummaryPipeline",
        {
            "num_pages": len(image_buffers),
        },
    )

    final_result = []
    page: dict = {}
    for index, image in enumerate(image_buffers):
        each_page_result = summarize_each_page(image, index + 1)
        final_result.append(each_page_result)

        epr_parse = safe_json_parse(each_page_result) or {}

        key_point = epr_parse.get("key_points", [])
        page[f"page_{index+1}"] = key_point

        epr_blob_path = (
            f"summary-post-announcement/each-{post_content_id}-{file_index + 1}-{index + 1}.json"
        )
        epr_blob_url = upload_json_to_blob(
            container_name="ai-summary",
            blob_path=epr_blob_path,
            data=epr_parse,
        )

        logger.log(
            "Uploaded summary JSON to blob",
            "PostSummaryPipeline",
            {"blob_url": epr_blob_url},
        )

    logger.log(
        "Process Each Page Summary Done",
        "PostSummaryPipeline",
    )

    all_page_text = json_all_page(final_result)

    file_text = (
        f"file {file_info.get('original_name')}, file_type - {file_info.get('file_type')} : {all_page_text} \n"
    )

    return {
        "success": True,
        "file_text": file_text,
        "all_page_text": all_page_text,
        "page_count": len(image_buffers),
        "page": page,
    }
