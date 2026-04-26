from google.cloud import storage
from app.core.config import settings

_storage_client: storage.Client | None = None

def get_storage_client() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=settings.PROJECT_ID)
    return _storage_client