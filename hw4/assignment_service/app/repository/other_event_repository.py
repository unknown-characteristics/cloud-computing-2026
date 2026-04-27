from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosResourceExistsError

from app.core.datastore_client import get_container
from app.models.other_event import OtherEvent

KIND = "other-events"

class OtherEventRepository:
    def __init__(self):
        # Gets or creates the Cosmos container for idempotency tracking
        self._container = get_container(KIND)

    def exists(self, event_id: str) -> bool:
        try:
            # Attempt to read by event_id (which we will use as the document id)
            self._container.read_item(item=event_id, partition_key=event_id)
            return True
        except CosmosResourceNotFoundError:
            return False

    def create(self, event_id: str) -> OtherEvent:
        # Use event_id as the Cosmos document 'id' property as well
        event = OtherEvent(id=event_id, event_id=event_id)
        data = event.model_dump()
        
        try:
            # create_item throws an error if it already exists, enforcing our check
            self._container.create_item(data)
        except CosmosResourceExistsError:
            raise ValueError(f"OtherEvent with event_id '{event_id}' already exists")

        return event