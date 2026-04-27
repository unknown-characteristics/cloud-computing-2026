import uuid, json
from datetime import datetime, timezone
from typing import Optional
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from app.core.datastore_client import get_container
from app.models.assignment import Assignment
from app.models.outbox import OutboxEvent

# Unified container name
CONTAINER_NAME = "asgn-data"

class StoreRepository:
    def __init__(self):
        # The container should be created with '/partition_id' as the Partition Key
        self._container = get_container(CONTAINER_NAME, partition_key_path="/partition_id")

    def create_with_outbox(self, id: str, assignment: Assignment) -> Assignment:
        """
        ATOMIC TRANSACTION: Creates an Assignment and an OutboxEvent in one batch.
        """
        now = datetime.now(timezone.utc)
        
        # 1. Setup Assignment
        assignment_id = id
        assignment.id = assignment_id
        assignment.created_at = now
        assignment.updated_at = now
        
        asgn_data = assignment.model_dump()
        self._convert_datetimes(asgn_data)
        asgn_data["partition_id"] = assignment_id
        asgn_data["doc_type"] = "assignment"
        # 2. Setup Outbox Event
        event_data = json.dumps({"assignment_id": assignment.id, "name": assignment.name, "creator_id": assignment.creator_id})
        outbox_event = OutboxEvent(
            id=str(uuid.uuid4()),
            partition_id=assignment_id, # MUST match assignment's partition_id
            data=event_data,
            event_id=str(uuid.uuid4()),
            event_type="assignment.created",
            pending=True
        )
        outbox_data = outbox_event.model_dump()
        outbox_data["partition_id"] = assignment_id
        outbox_data["doc_type"] = "outbox"
        # 3. Execute Transactional Batch
        # Both items belong to the same partition (assignment_id)
        operations = [
            ("create", (asgn_data,), {}),
            ("create", (outbox_data,), {})
        ]

        # 4. Execute Transaction
        # All items in 'operations' must share the partition_key passed here
        results = self._container.execute_item_batch(
            batch_operations=operations, 
            partition_key=assignment_id
        )

        # Check for errors in the batch results
        for res in results:
            if res.get("statusCode") >= 400:
                raise Exception(f"Transaction failed: {res}")

        return assignment

    def get_assignment_by_id(self, assignment_id: str) -> Optional[Assignment]:
        try:
            # We use the assignment_id as both item ID and partition key
            item = self._container.read_item(item=assignment_id, partition_key=assignment_id)
            if item.get("doc_type") == "assignment":
                return Assignment(**item)
            return None
        except CosmosResourceNotFoundError:
            return None

    def get_pending_outbox_events(self) -> list[OutboxEvent]:
        # Filter by doc_type and pending status
        items = list(self._container.query_items(
            query="SELECT * FROM c WHERE c.doc_type = 'outbox' AND c.pending = true",
            enable_cross_partition_query=True
        ))
        return [OutboxEvent(**item) for item in items]

    def mark_outbox_published(self, event_id: str, partition_id: str) -> None:
        """
        Updates an outbox event. Requires partition_id (assignment_id) to find the item.
        """
        try:
            item = self._container.read_item(item=event_id, partition_key=partition_id)
            item["pending"] = False
            self._container.upsert_item(item)
        except CosmosResourceNotFoundError:
            return

    def get_all_assignments(self) -> list[Assignment]:
        items = list(self._container.query_items(
            query="SELECT * FROM c WHERE c.doc_type = 'assignment'",
            enable_cross_partition_query=True
        ))
        return [Assignment(**item) for item in items]
    
    def get_all_assignments_by_creator_id(self, creator_id: int) -> list[Assignment]:
        items = list(self._container.query_items(
            query="SELECT * FROM c WHERE c.doc_type = 'assignment' AND c.creator_id = @creator_id",
            parameters=[{"name": "@creator_id", "value": creator_id}],
            enable_cross_partition_query=True
        ))
        return [Assignment(**item) for item in items]

    def _convert_datetimes(self, data: dict):
        """Helper to ensure all datetime objects are ISO strings for Cosmos JSON."""
        for k, v in data.items():
            if isinstance(v, datetime):
                data[k] = v.isoformat()

    def update_assignment(self, assignment_id: str, fields: dict) -> Optional[Assignment]:
        try:
            item = self._container.read_item(item=assignment_id, partition_key=assignment_id)
            if item["doc_type"] != "assignment":
                return None
            fields["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            for k, v in fields.items():
                if isinstance(v, datetime):
                    fields[k] = v.isoformat()
            
            item.update(fields)
            
            # Prepare the Outbox item
            outbox_id = str(uuid.uuid4())
            outbox_data = {
                "id": outbox_id,
                "partition_id": assignment_id, # Shared PK
                "doc_type": "outbox",
                "event_id": str(uuid.uuid4()),
                "event_type": "assignment.updated",
                "data": json.dumps({
                    "assignment_id": assignment_id, 
                    "name": item.get("name"), 
                    "creator_id": item.get("creator_id")
                }),
                "pending": True
            }

            # 3. Define Batch Operations
            # Using 'upsert' for the assignment update and 'create' for the outbox
            operations = [
                ("upsert", (item,), {}),
                ("create", (outbox_data,), {})
            ]

            # 4. Execute Transaction
            results = self._container.execute_item_batch(
                batch_operations=operations, 
                partition_key=assignment_id
            )

            # Check results
            for res in results:
                if res.get("statusCode") >= 400:
                    raise Exception(f"Update transaction failed: {res}")

            return Assignment(**item)
        except CosmosResourceNotFoundError:
            return None

    def delete_with_outbox(self, assignment_id: str):
        """
        Atomically deletes an assignment and records the deletion in the outbox.
        """
        outbox_data = {
            "id": str(uuid.uuid4()),
            "partition_id": assignment_id, # Shared PK
            "doc_type": "outbox",
            "event_id": str(uuid.uuid4()),
            "event_type": "assignment.deleted",
            "data": json.dumps({
                    "assignment_id": assignment_id
                }),
            "pending": True
        }

        # 2. Define Operations
        operations = [
            ("delete", (assignment_id,), {}),
            ("create", (outbox_data,), {})
        ]

        try:
            # 3. Execute Transaction
            results = self._container.execute_item_batch(
                batch_operations=operations, 
                partition_key=assignment_id
            )

            for res in results:
                if res.get("statusCode") >= 400:
                    # If delete fails because it's not found, handle gracefully
                    if res.get("statusCode") == 404: return False
                    raise Exception(f"Delete transaction failed: {res}")

            return True
        except CosmosResourceNotFoundError:
            return False
