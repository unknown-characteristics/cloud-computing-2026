from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from app.core.config import settings

_blob_service_client: BlobServiceClient | None = None

def get_blob_service_client() -> BlobServiceClient:
    global _blob_service_client
    if _blob_service_client is None:
        credential = DefaultAzureCredential()
        _blob_service_client = BlobServiceClient(
            account_url=f"https://{settings.azure_storage_account_name}.blob.core.windows.net",
            credential=credential,
        )
    return _blob_service_client
