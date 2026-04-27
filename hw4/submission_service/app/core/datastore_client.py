from functools import lru_cache
from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy
from azure.identity import DefaultAzureCredential
from app.core.config import settings

@lru_cache(maxsize=1)
def _cosmos_client() -> CosmosClient:
    return CosmosClient(
        url=settings.cosmos_endpoint,
        credential=DefaultAzureCredential(),
    )

@lru_cache(maxsize=1)
def get_datastore_client() -> DatabaseProxy:
    client = _cosmos_client()
    # Simply get the database, do not attempt to create it
    return client.get_database_client(settings.cosmos_database)

@lru_cache(maxsize=16)
def get_container(name: str, partition_key_path: str = "/id") -> ContainerProxy:
    db = get_datastore_client()
    # Simply get the container, do not attempt to create it
    return db.get_container_client(name)
