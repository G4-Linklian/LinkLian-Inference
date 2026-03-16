from app.core.file import load_image_from_url, safe_json_parse
from app.core.logger import AppLogger
from app.services.blob.blob_storage import upload_json_to_blob
from app.services.llm.summary.summary import summarize_each_page

logger = AppLogger()


def process_image_summary(post_content_id: str, file_index: int, file_info: dict) -> dict:
	logger.log(
		"Processing Image type",
		"PostSummaryPipeline",
	)

	page: dict = {}

	azure_path = file_info.get("file_url")
	image_bytes = load_image_from_url(azure_path)

	each_page_result = summarize_each_page(image_bytes, 1)

	epr_parse = safe_json_parse(each_page_result) or {}

	key_point = epr_parse.get("key_points", [])
	page[f"{1}"] = key_point

	logger.debug(
		"Parsed summary result for image file",
		"PostSummaryPipeline",
		{
			"epr_parse": epr_parse,
		},
	)

	epr_blob_path = f"summary-post-announcement/each-{post_content_id}-{file_index + 1}-0.json"
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

	file_text = (
		f"file {file_info.get('original_name')}, file_type - {file_info.get('file_type')} : {each_page_result} \n"
	)

	return {
		"success": True,
		"file_text": file_text,
		"page": page,
		"page_count": 1,
	}
