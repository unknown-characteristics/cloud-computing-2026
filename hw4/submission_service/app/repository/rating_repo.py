from typing import Optional, List
from app.models.rating import Rating
from app.helpers.datetime_helpers import utcnow
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from app.core.datastore_client import get_container
from app.models.outbox import OutboxEvent
import uuid, json
from datetime import datetime, timezone

CONTAINER_NAME = "subm-ratings-data"

class RatingRepository:
    # --- Helper to build a deterministic key for uniqueness ---
    def _build_key(self, submission_id: str, user_id: str):
        # Example: one rating per user per submission
        return f"rating_key_{submission_id}_{user_id}"

    # # --- Create a rating ---
    # def create(self, rating: Rating) -> Rating:
    #     key = self._build_key(rating.submission_id, str(rating.user_id))

    #     # Prevent overwrite
    #     old = self._client.get(key)
    #     if old is not None and old["status"] != "deleted":
    #         raise ValueError(
    #             f"Rating already exists for submission_id={rating.submission_id} "
    #             f"and user_id={rating.user_id}"
    #         )

    #     rating.created_at = rating.updated_at = utcnow()

    #     entity = datastore.Entity(key=key)
    #     entity.update(rating.model_dump(exclude={"id"}))

    #     self._client.put(entity)
    #     rating.id = key.name  # deterministic string key
    #     return rating

    # # --- Get rating by ID ---
    # def get_by_id(self, rating_id: str) -> Optional[Rating]:
    #     key = self._client.key(self._kind, rating_id)
    #     entity = self._client.get(key)
    #     if not entity or entity.get("status") == "deleted":
    #         return None
    #     return self._build_rating(entity)

    # # --- Get all active ratings for a submission ---
    # def get_active_by_submission(self, submission_id: str) -> List[Rating]:
    #     query = self._client.query(kind=self._kind)
    #     query.add_filter("submission_id", "=", submission_id)
    #     query.add_filter("status", "=", "active")
    #     entities = list(query.fetch())
    #     return [self._build_rating(e) for e in entities]

    # # --- Update fields for a rating ---
    # def update(self, rating_id: str, fields: dict) -> Rating:
    #     key = self._client.key(self._kind, rating_id)
    #     entity = self._client.get(key)
    #     if not entity:
    #         raise ValueError(f"Rating with id {rating_id} not found")

    #     fields["updated_at"] = utcnow()
    #     entity.update(fields)
    #     self._client.put(entity)
    #     return self._build_rating(entity)

    # # --- Helper to construct Rating safely ---
    # def _build_rating(self, entity) -> Rating:
    #     data = {k: v for k, v in entity.items() if k != "id"}
    #     return Rating(id=entity.key.name, **data)

    def __init__(self):
        # The container should be created with '/partition_id' as the Partition Key
        self._container = get_container(CONTAINER_NAME, partition_key_path="/partition_id")

    def _get_log_event(self, rating_id: str, sub_id: str, extra: dict = None):
        data = {"rating_id": rating_id, "submission_id": sub_id}
        if extra: data.update(extra)
        return json.dumps(data)

    def create_with_outbox(self, rating: Rating) -> Rating:
        """
        ATOMIC TRANSACTION: Creates an Submission and an OutboxEvent in one batch.
        """
        now = datetime.now(timezone.utc)
        
        # 1. Setup Submission
        rating_id = self._build_key(rating.submission_id, rating.user_id)
        rating.id = rating_id

        old = self.get_rating_by_id(rating_id)
        if old is not None and old.status != "deleted":
            raise ValueError(
                f"Rating already exists for submission_id={rating.submission_id} "
                f"and user_id={rating.user_id}"
            )

        rating.created_at = now
        rating.updated_at = now
        
        rating_data = rating.model_dump()
        self._convert_datetimes(rating_data)
        rating_data["partition_id"] = rating_id
        rating_data["doc_type"] = "rating"
        # 2. Setup Outbox Event
        event_data = self._get_log_event(rating.id, rating.submission_id)
        outbox_event = OutboxEvent(
            id=str(uuid.uuid4()),
            partition_id=rating_id, # MUST match rating's partition_id
            data=event_data,
            event_id=str(uuid.uuid4()),
            event_type="rating.created",
            pending=True
        )
        outbox_data = outbox_event.model_dump()
        outbox_data["partition_id"] = rating_id
        outbox_data["doc_type"] = "outbox"
        # 3. Execute Transactional Batch
        # Both items belong to the same partition (rating_id)
        operations = [
            ("upsert", (rating_data,), {}),
            ("create", (outbox_data,), {})
        ]

        # 4. Execute Transaction
        # All items in 'operations' must share the partition_key passed here
        results = self._container.execute_item_batch(
            batch_operations=operations, 
            partition_key=rating_id
        )

        # Check for errors in the batch results
        for res in results:
            if res.get("statusCode") >= 400:
                raise Exception(f"Transaction failed: {res}")

        return rating

    def get_rating_by_id(self, rating_id: str) -> Optional[Rating]:
        try:
            # We use the rating_id as both item ID and partition key
            item = self._container.read_item(item=rating_id, partition_key=rating_id)
            if item.get("doc_type") == "rating" and item.get("status") != "deleted":
                return Rating(**item)
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

    def get_all_ratings(self) -> list[Rating]:
        items = list(self._container.query_items(
            query="SELECT * FROM c WHERE c.doc_type = 'rating'",
            enable_cross_partition_query=True
        ))
        return [Rating(**item) for item in items]

    def get_all_active_ratings_by_submission_id(self, submission_id: str) -> list[Rating]:
        items = list(self._container.query_items(
            query="SELECT * FROM c WHERE c.doc_type = 'rating' AND c.submission_id = @submission_id AND c.status = 'active'",
            parameters=[{"name": "@submission_id", "value": submission_id}],
            enable_cross_partition_query=True
        ))
        return [Rating(**item) for item in items]

    def _convert_datetimes(self, data: dict):
        """Helper to ensure all datetime objects are ISO strings for Cosmos JSON."""
        for k, v in data.items():
            if isinstance(v, datetime):
                data[k] = v.isoformat()

    def update_rating(self, rating_id: str, fields: dict) -> Optional[Rating]:
        try:
            item = self._container.read_item(item=rating_id, partition_key=rating_id)
            if item["doc_type"] != "rating":
                return None
            fields["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            for k, v in fields.items():
                if isinstance(v, datetime):
                    fields[k] = v.isoformat()
            
            item.update(fields)
            event_type = "rating.deleted" if "status" in fields and fields["status"] == "deleted" else "rating.updated"

            submission_id = item.get("submission_id")
            # Prepare the Outbox item
            outbox_id = str(uuid.uuid4())
            outbox_data = {
                "id": outbox_id,
                "partition_id": rating_id, # Shared PK
                "doc_type": "outbox",
                "event_id": str(uuid.uuid4()),
                "event_type": event_type,
                "data": self._get_log_event(rating_id, submission_id),
                "pending": True
            }

            # 3. Define Batch Operations
            # Using 'upsert' for the rating update and 'create' for the outbox
            operations = [
                ("upsert", (item,), {}),
                ("create", (outbox_data,), {})
            ]

            # 4. Execute Transaction
            results = self._container.execute_item_batch(
                batch_operations=operations, 
                partition_key=rating_id
            )

            # Check results
            for res in results:
                if res.get("statusCode") >= 400:
                    raise Exception(f"Update transaction failed: {res}")

            return Rating(**item)
        except CosmosResourceNotFoundError:
            return None
