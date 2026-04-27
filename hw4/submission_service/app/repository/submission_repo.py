from typing import Optional
from datetime import datetime, timezone
from app.models.submission import Submission
from app.helpers.datetime_helpers import utcnow
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from app.core.datastore_client import get_container
from app.models.outbox import OutboxEvent
import uuid, json

CONTAINER_NAME = "subm-submissions-data"

class SubmissionRepository:
    def _build_key(self, user_id: int, assignment_id: str):
        # Deterministic composite key → guarantees uniqueness
        return f"subm_key_{user_id}_{assignment_id}"

    # def create(self, sub: Submission) -> Submission:
    #     key = self._build_key(sub.user_id, sub.assignment_id)

    #     # Prevent overwrite (optional but recommended)
    #     old = self._client.get(key)
    #     if old is not None and old["status"] != "deleted":
    #         raise ValueError(
    #             f"Submission already exists for user_id={sub.user_id} "
    #             f"and assignment_id={sub.assignment_id}"
    #         )

    #     sub.created_at = sub.updated_at = utcnow()

    #     entity = datastore.Entity(key=key)
    #     entity.update(sub.model_dump(exclude={"id"}))

    #     self._client.put(entity)

    #     # Key is string-based now
    #     sub.id = key.name
    #     return sub

    # def get_by_id(self, sub_id: str) -> Optional[Submission]:
    #     key = self._client.key(self._kind, sub_id)
    #     entity = self._client.get(key)

    #     if not entity or entity.get("status") == "deleted":
    #         return None

    #     return Submission(id=entity.key.name, **entity)

    # def get_all_active_by_assignment(self, assignment_id: str) -> list[Submission]:
    #     query = self._client.query(kind=self._kind)
    #     query.add_filter("assignment_id", "=", assignment_id)
    #     query.add_filter("status", "=", "active")

    #     entities = list(query.fetch())
    #     return [Submission(id=e.key.name, **e) for e in entities]
    #     # out =  [Submission(id=e.key.name, **{k: v for k, v in e.items() if k != "id"}) for e in entities]
    #     # print(entities[0].key)
    #     # print(out)
    #     # print(out[0].model_dump())
    #     # print(entities[0].key.name)
    #     # return out

    # def get_all_active_by_user(self, user_id: int) -> list[Submission]:
    #     query = self._client.query(kind=self._kind)
    #     query.add_filter("user_id", "=", user_id)
    #     query.add_filter("status", "=", "active")

    #     entities = list(query.fetch())
    #     return [Submission(id=e.key.name, **e) for e in entities]

    # def update(self, sub_id: str, fields: dict) -> Submission:
    #     fields["updated_at"] = utcnow()

    #     key = self._client.key(self._kind, sub_id)
    #     entity = self._client.get(key)

    #     if not entity:
    #         raise ValueError(f"Submission with id {sub_id} not found")

    #     entity.update(fields)
    #     self._client.put(entity)

    #     return Submission(id=entity.key.name, **entity)

    # def get_all(self):
    #     query = self.client.query(kind=self.kind)
    #     results = list(query.fetch())

    #     submissions = []
    #     for r in results:
    #         sub = Submission(**r)
    #         # Datastore pune ID-ul in key, trebuie sa il scoatem
    #         sub.id = r.key.name
    #         submissions.append(sub)

    #     return submissions

    def __init__(self):
        # The container should be created with '/partition_id' as the Partition Key
        self._container = get_container(CONTAINER_NAME, partition_key_path="/partition_id")

    def _get_log_event(self, sub_id: str, assign_id: str, extra: dict = None):
        data = {"submission_id": sub_id, "assignment_id": assign_id}
        if extra: data.update(extra)
        return json.dumps(data)

    def create_with_outbox(self, submission: Submission) -> Submission:
        """
        ATOMIC TRANSACTION: Creates an Submission and an OutboxEvent in one batch.
        """
        now = datetime.now(timezone.utc)
        
        # 1. Setup Submission
        submission_id = self._build_key(submission.user_id, submission.assignment_id)
        submission.id = submission_id

        old = self.get_submission_by_id(submission_id)
        if old is not None and old.status != "deleted":
            raise ValueError(
                f"Submission already exists for user_id={submission.user_id} "
                f"and assignment_id={submission.assignment_id}"
            )

        submission.created_at = now
        submission.updated_at = now
        
        subm_data = submission.model_dump()
        self._convert_datetimes(subm_data)
        subm_data["partition_id"] = submission_id
        subm_data["doc_type"] = "submission"
        # 2. Setup Outbox Event
        event_data = self._get_log_event(submission.id, submission.assignment_id)
        outbox_event = OutboxEvent(
            id=str(uuid.uuid4()),
            partition_id=submission_id, # MUST match submission's partition_id
            data=event_data,
            event_id=str(uuid.uuid4()),
            event_type="submission.created",
            pending=True
        )
        outbox_data = outbox_event.model_dump()
        outbox_data["partition_id"] = submission_id
        outbox_data["doc_type"] = "outbox"
        # 3. Execute Transactional Batch
        # Both items belong to the same partition (submission_id)
        operations = [
            ("upsert", (subm_data,), {}),
            ("create", (outbox_data,), {})
        ]

        # 4. Execute Transaction
        # All items in 'operations' must share the partition_key passed here
        results = self._container.execute_item_batch(
            batch_operations=operations, 
            partition_key=submission_id
        )

        # Check for errors in the batch results
        for res in results:
            if res.get("statusCode") >= 400:
                raise Exception(f"Transaction failed: {res}")

        return submission

    def get_submission_by_id(self, submission_id: str) -> Optional[Submission]:
        try:
            # We use the submission_id as both item ID and partition key
            item = self._container.read_item(item=submission_id, partition_key=submission_id)
            if item.get("doc_type") == "submission" and item.get("status") != "deleted":
                return Submission(**item)
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
        Updates an outbox event. Requires partition_id (submission_id) to find the item.
        """
        try:
            item = self._container.read_item(item=event_id, partition_key=partition_id)
            item["pending"] = False
            self._container.upsert_item(item)
        except CosmosResourceNotFoundError:
            return

    def get_all_submissions(self) -> list[Submission]:
        items = list(self._container.query_items(
            query="SELECT * FROM c WHERE c.doc_type = 'submission'",
            enable_cross_partition_query=True
        ))
        return [Submission(**item) for item in items]
    
    def get_all_active_submissions_by_creator_id(self, creator_id: int) -> list[Submission]:
        items = list(self._container.query_items(
            query="SELECT * FROM c WHERE c.doc_type = 'submission' AND c.user_id = @creator_id AND c.status = 'active'",
            parameters=[{"name": "@creator_id", "value": creator_id}],
            enable_cross_partition_query=True
        ))
        return [Submission(**item) for item in items]

    def get_all_active_submissions_by_assignment_id(self, assignment_id: str) -> list[Submission]:
        items = list(self._container.query_items(
            query="SELECT * FROM c WHERE c.doc_type = 'submission' AND c.assignment_id = @assignment_id AND c.status = 'active'",
            parameters=[{"name": "@assignment_id", "value": assignment_id}],
            enable_cross_partition_query=True
        ))
        return [Submission(**item) for item in items]

    def _convert_datetimes(self, data: dict):
        """Helper to ensure all datetime objects are ISO strings for Cosmos JSON."""
        for k, v in data.items():
            if isinstance(v, datetime):
                data[k] = v.isoformat()

    def update_submission(self, submission_id: str, fields: dict) -> Optional[Submission]:
        try:
            item = self._container.read_item(item=submission_id, partition_key=submission_id)
            if item["doc_type"] != "submission":
                return None
            fields["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            for k, v in fields.items():
                if isinstance(v, datetime):
                    fields[k] = v.isoformat()
            
            item.update(fields)
            event_type = "submission.deleted" if "status" in fields and fields["status"] == "deleted" else "submission.updated"

            assignment_id = item.get("assignment_id")
            # Prepare the Outbox item
            outbox_id = str(uuid.uuid4())
            outbox_data = {
                "id": outbox_id,
                "partition_id": submission_id, # Shared PK
                "doc_type": "outbox",
                "event_id": str(uuid.uuid4()),
                "event_type": event_type,
                "data": self._get_log_event(submission_id, assignment_id),
                "pending": True
            }

            # 3. Define Batch Operations
            # Using 'upsert' for the submission update and 'create' for the outbox
            operations = [
                ("upsert", (item,), {}),
                ("create", (outbox_data,), {})
            ]

            # 4. Execute Transaction
            results = self._container.execute_item_batch(
                batch_operations=operations, 
                partition_key=submission_id
            )

            # Check results
            for res in results:
                if res.get("statusCode") >= 400:
                    raise Exception(f"Update transaction failed: {res}")

            return Submission(**item)
        except CosmosResourceNotFoundError:
            return None

    # def delete_with_outbox(self, submission_id: str):
    #     """
    #     Atomically deletes a submission and records the deletion in the outbox.
    #     """
    #     assignment_id = submission_id.split("_")[-1]
    #     outbox_data = {
    #         "id": str(uuid.uuid4()),
    #         "partition_id": submission_id, # Shared PK
    #         "doc_type": "outbox",
    #         "event_id": str(uuid.uuid4()),
    #         "event_type": "submission.deleted",
    #         "data": self._get_log_event(submission_id, assignment_id),
    #         "pending": True
    #     }

    #     # 2. Define Operations
    #     operations = [
    #         ("delete", (submission_id,), {}),
    #         ("create", (outbox_data,), {})
    #     ]

    #     try:
    #         # 3. Execute Transaction
    #         results = self._container.execute_item_batch(
    #             batch_operations=operations, 
    #             partition_key=submission_id
    #         )

    #         for res in results:
    #             if res.get("statusCode") >= 400:
    #                 # If delete fails because it's not found, handle gracefully
    #                 if res.get("statusCode") == 404: return False
    #                 raise Exception(f"Delete transaction failed: {res}")

    #         return True
    #     except CosmosResourceNotFoundError:
    #         return False
