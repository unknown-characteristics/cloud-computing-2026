import uuid
from typing import Optional
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.core.datastore_client import get_container
from app.models.outbox import OutboxEvent

KIND = "outbox"

class OutboxRepository:
    def __init__(self):
        # Gets or creates the Cosmos container for the outbox
        self._container = get_container(KIND)

    def create(self, event: OutboxEvent) -> OutboxEvent:
        # Cosmos DB requires the document 'id' to be a string
        event.id = str(uuid.uuid4())
        
        data = event.model_dump()
        self._container.upsert_item(data)
        
        return event

    def get_pending(self) -> list[OutboxEvent]:
        # Standard Cosmos DB SQL query
        items = list(self._container.query_items(
            query="SELECT * FROM c WHERE c.pending = true",
            enable_cross_partition_query=True
        ))
        return [OutboxEvent(**item) for item in items]

    def mark_as_published(self, event_id: str) -> None:
        try:
            # Fetch by document ID and partition key
            item = self._container.read_item(item=event_id, partition_key=event_id)
            item["pending"] = False
            self._container.upsert_item(item)
        except CosmosResourceNotFoundError:
            return

    def get_all(self) -> list[OutboxEvent]:
        items = list(self._container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        return [OutboxEvent(**item) for item in items]