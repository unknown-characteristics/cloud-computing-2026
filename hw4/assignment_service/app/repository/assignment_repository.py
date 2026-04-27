import uuid
from datetime import datetime, timezone
from typing import Optional
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.core.datastore_client import get_container
from app.models.assignment import Assignment

KIND = "asgn-assignments"

class AssignmentRepository:
    def __init__(self):
        self._container = get_container(KIND)

    def create(self, assignment: Assignment) -> Assignment:
        now = datetime.now(timezone.utc)
        assignment.created_at = now
        assignment.updated_at = now

        # Cosmos DB strictly requires a string ID
        assignment.id = str(uuid.uuid4())

        data = assignment.model_dump()
        # Cosmos DB requires datetime fields to be formatted as ISO strings in JSON
        for k, v in data.items():
            if isinstance(v, datetime):
                data[k] = v.isoformat()

        self._container.upsert_item(data)
        return assignment

    def get_by_id(self, assignment_id: int | str) -> Optional[Assignment]:
        try:
            item = self._container.read_item(item=str(assignment_id), partition_key=str(assignment_id))
            return Assignment(**item)
        except CosmosResourceNotFoundError:
            return None

    def get_all(self) -> list[Assignment]:
        items = list(self._container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        return [Assignment(**item) for item in items]
    
    def get_all_by_creator_id(self, creator_id: int | str) -> list[Assignment]:
        items = list(self._container.query_items(
            query="SELECT * FROM c WHERE c.creator_id = @creator_id",
            parameters=[{"name": "@creator_id", "value": int(creator_id)}],
            enable_cross_partition_query=True
        ))
        return [Assignment(**item) for item in items]

    def update(self, assignment_id: int | str, fields: dict) -> Optional[Assignment]:
        try:
            item = self._container.read_item(item=str(assignment_id), partition_key=str(assignment_id))
            fields["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            for k, v in fields.items():
                if isinstance(v, datetime):
                    fields[k] = v.isoformat()
            
            item.update(fields)
            self._container.upsert_item(item)
            return Assignment(**item)
        except CosmosResourceNotFoundError:
            return None

    def delete(self, assignment_id: int | str) -> bool:
        try:
            self._container.delete_item(item=str(assignment_id), partition_key=str(assignment_id))
            return True
        except CosmosResourceNotFoundError:
            return False