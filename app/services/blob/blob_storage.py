import json
import os

from azure.storage.blob import BlobServiceClient, ContentSettings

from app.core.logger import AppLogger

logger = AppLogger()

_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")

blob_service_client = BlobServiceClient.from_connection_string(_connection_string)


def upload_json_to_blob(
    container_name: str,
    blob_path: str,
    data: dict | list,
) -> str:
    """
    Upload a Python dict/list as a JSON file to Azure Blob Storage.
    Returns the public URL of the uploaded blob.
    """
    container_client = blob_service_client.get_container_client(container_name)

    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

    blob_client = container_client.get_blob_client(blob_path)
    blob_client.upload_blob(
        json_bytes,
        overwrite=True,
        content_settings=ContentSettings(content_type="application/json"),
    )

    logger.log(
        "Uploaded JSON to blob",
        "BlobStorageService",
        {"container": container_name, "blob_path": blob_path, "size": len(json_bytes)},
    )

    return blob_client.url


def upload_text_to_blob(
    container_name: str,
    blob_path: str,
    text: str,
) -> str:
    """
    Upload a plain text string to Azure Blob Storage.
    Returns the public URL of the uploaded blob.
    """
    container_client = blob_service_client.get_container_client(container_name)

    text_bytes = text.encode("utf-8")

    blob_client = container_client.get_blob_client(blob_path)
    blob_client.upload_blob(
        text_bytes,
        overwrite=True,
        content_settings=ContentSettings(content_type="text/plain; charset=utf-8"),
    )

    logger.log(
        "Uploaded text to blob",
        "BlobStorageService",
        {"container": container_name, "blob_path": blob_path, "size": len(text_bytes)},
    )

    return blob_client.url
