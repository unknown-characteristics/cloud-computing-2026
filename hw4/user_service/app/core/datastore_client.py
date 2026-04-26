"""
Azure Cosmos DB (NoSQL API) client — the closest Azure equivalent to Google
Cloud Datastore.

Mapping vs. the old Datastore client:
    project   ->  Cosmos account (implicit in the endpoint URL)
    database  ->  Cosmos database
    namespace ->  Cosmos container (one container per "namespace" / kind)

Auth: DefaultAzureCredential picks the App Service Managed Identity in
production and falls back to the Azure CLI / env vars locally. The identity
needs the `Cosmos DB Built-in Data Contributor` role on the account.

Public API kept intentionally similar to the old helper:
    get_datastore_client()   -> DatabaseProxy   (≈ datastore.Client)
    get_container("users")   -> ContainerProxy  (≈ a Datastore namespace/kind)
"""
from functools import lru_cache

from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy, PartitionKey
from azure.cosmos.exceptions import CosmosResourceExistsError
from azure.identity import DefaultAzureCredential

from helpers.settings import settings


@lru_cache(maxsize=1)
def _cosmos_client() -> CosmosClient:
    """One CosmosClient per process — it is thread-safe and pools internally."""
    return CosmosClient(
        url=settings.cosmos_endpoint,
        credential=DefaultAzureCredential(),
    )


@lru_cache(maxsize=1)
def get_datastore_client() -> DatabaseProxy:
    """Return a handle to the configured Cosmos database.

    Equivalent to the old `datastore.Client(project=..., database=...)`.
    """
    client = _cosmos_client()
    return client.create_database_if_not_exists(id=settings.cosmos_database)


@lru_cache(maxsize=16)
def get_container(name: str, partition_key_path: str = "/id") -> ContainerProxy:
    """Return (creating if missing) a Cosmos container.

    Replaces the Datastore "namespace" concept — one container per kind/namespace.
    Defaults to `/id` as the partition key, which matches Datastore's
    key-by-id behaviour for low-cardinality lookups. For high-write entities
    pass a more selective partition key path.
    """
    db = get_datastore_client()
    try:
        return db.create_container(
            id=name,
            partition_key=PartitionKey(path=partition_key_path),
        )
    except CosmosResourceExistsError:
        return db.get_container_client(name)
