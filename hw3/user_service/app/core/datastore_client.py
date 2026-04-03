from google.cloud import datastore
from helpers.settings import settings

_client: datastore.Client | None = None


def get_datastore_client() -> datastore.Client:
    global _client
    if _client is None:
        _client = datastore.Client(project=settings.PROJECT_ID, namespace="users", database="cloud-hw1")
    return _client
