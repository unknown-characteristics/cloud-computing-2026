from google.cloud import firestore
from app.core.config import settings

_client: firestore.AsyncClient | None = None

def get_firestore_client() -> firestore.AsyncClient:
    global _client
    if _client is None:
        _client = firestore.AsyncClient(project=settings.FIRESTORE_PROJECT_ID)
    return _client