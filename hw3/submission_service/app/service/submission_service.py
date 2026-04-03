import json, uuid
from fastapi import HTTPException, UploadFile
from app.dtos.submission_dto import SubmissionResponseDTO
from app.models.submission import Submission
from app.models.outbox import OutboxEvent
from app.repository.submission_repo import SubmissionRepository
from app.repository.outbox_repo import OutboxRepository
from app.helpers.datetime_helpers import utcnow
from app.core.storage_client import get_storage_client
from app.core.config import settings
from app.service.outbox_service import OutboxService
from app.service.rating_service import RatingService

class SubmissionService:
    def __init__(self):
        self._repo = SubmissionRepository()
        self._outbox = OutboxRepository()

    async def create(self, assignment_id: int, user_id: int, file: UploadFile) -> SubmissionResponseDTO:
        client = get_storage_client()
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "bin"
        filename = f"submissions/{assignment_id}/{user_id}_{uuid.uuid4().hex}.{ext}"

        blob = bucket.blob(filename)
        content = await file.read()
        blob.upload_from_string(content, content_type=file.content_type)

        try:
            sub = self._repo.create(Submission(
                user_id=user_id,
                assignment_id=assignment_id,
                filepath=filename
            ))
        except ValueError as e:
            if "Submission already exists" in e.args[0]:
                raise HTTPException(status_code=400, detail=e.args[0])

        self._log_event(sub.id, sub.assignment_id, "submission.created")
        await OutboxService().process_pending_events()
        return SubmissionResponseDTO(**sub.model_dump())

    def get_all_by_assignment(self, assignment_id: int) -> list[SubmissionResponseDTO]:
        subs = self._repo.get_all_active_by_assignment(assignment_id)
        return [SubmissionResponseDTO(**s.model_dump()) for s in subs]

    def get_all_by_user(self, user_id: int) -> list[SubmissionResponseDTO]:
        subs = self._repo.get_all_active_by_user(user_id)
        return [SubmissionResponseDTO(**s.model_dump()) for s in subs]

    def get_file(self, sub_id: str) -> tuple[bytes, str, str]:
        sub = self._repo.get_by_id(sub_id)
        if not sub:
            raise HTTPException(status_code=404, detail="Submission not found")

        client = get_storage_client()
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        blob = bucket.blob(sub.filepath)
        if not blob.exists():
            raise HTTPException(status_code=404, detail="File not found in storage")

        file_bytes = blob.download_as_bytes()
        original_name = sub.filepath.split("/")[-1]
        return file_bytes, blob.content_type or "application/octet-stream", original_name

    async def update(self, sub_id: str, file: UploadFile, user_id: int) -> SubmissionResponseDTO:
        sub = self._repo.get_by_id(sub_id)
        if not sub:
            raise HTTPException(status_code=404, detail="Submission not found")
        if sub.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to edit this submission")

        client = get_storage_client()
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "bin"
        filename = f"submissions/{sub.assignment_id}/{user_id}_{uuid.uuid4().hex}.{ext}"

        blob = bucket.blob(filename)
        content = await file.read()
        blob.upload_from_string(content, content_type=file.content_type)

        updated = self._repo.update(sub_id, {"filepath": filename})
        self._log_event(sub_id, updated.assignment_id, "submission.updated", {"filepath": filename})
        await OutboxService().process_pending_events()
        return SubmissionResponseDTO(**updated.model_dump())

    async def delete(self, sub_id: str, user_id: int) -> None:
        sub = self._repo.get_by_id(sub_id)
        if not sub:
            raise HTTPException(status_code=404, detail="Submission not found")
        if sub.user_id != user_id and user_id != -1:
            raise HTTPException(status_code=403, detail="Not authorized to delete this submission")

        self._repo.update(sub_id, {"status": "deleted", "deleted_at": utcnow()})

        rating_service = RatingService()
        results = rating_service.get_by_submission(sub_id)
        for r in results:
            await rating_service.delete(r.id, -1)
        
        self._log_event(sub_id, sub.assignment_id, "submission.deleted")
        await OutboxService().process_pending_events()

    def _log_event(self, sub_id: str, assign_id: str, ev_type: str, extra: dict = None):
        data = {"submission_id": sub_id, "assignment_id": assign_id}
        if extra: data.update(extra)
        self._outbox.create(OutboxEvent(
            data=json.dumps(data), event_id=str(uuid.uuid4()), event_type=ev_type, pending=True
        ))

    def get_all_submissions(self):
        submissions = self.repo.get_all()
        result = []

        for sub in submissions:
            # Ascundem submisiile care au fost sterse (soft delete)
            if sub.status != "deleted":
                result.append(
                    SubmissionResponseDTO(
                        id=str(sub.id),
                        user_id=sub.user_id,
                        assignment_id=sub.assignment_id,
                        filepath=sub.filepath,
                        status=sub.status,
                        created_at=sub.created_at,
                        updated_at=sub.updated_at
                    )
                )
        return result