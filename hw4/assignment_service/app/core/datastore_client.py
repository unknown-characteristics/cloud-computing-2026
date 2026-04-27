from functools import lru_cache
from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy, PartitionKey
from azure.cosmos.exceptions import CosmosResourceExistsError
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
    return client.create_database_if_not_exists(id=settings.cosmos_database)

@lru_cache(maxsize=16)
def get_container(name: str, partition_key_path: str = "/id") -> ContainerProxy:
    db = get_datastore_client()
    try:
        return db.create_container(
            id=name,
            partition_key=PartitionKey(path=partition_key_path),
        )
    except CosmosResourceExistsError:
        return db.get_container_client(name)