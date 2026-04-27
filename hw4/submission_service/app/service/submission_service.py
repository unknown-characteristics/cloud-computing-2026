import uuid
from fastapi import HTTPException, UploadFile
from azure.storage.blob import ContentSettings  # Added for Azure content types

from app.dtos.submission_dto import SubmissionResponseDTO
from app.models.submission import Submission
from app.repository.submission_repo import SubmissionRepository
from app.helpers.datetime_helpers import utcnow
# Assuming you placed the new client method in the same storage_client file
from app.core.storage_client import get_blob_service_client 
from app.core.config import settings
from app.service.outbox_service import OutboxService
from app.service.rating_service import RatingService

class SubmissionService:
    def __init__(self):
        self._repo = SubmissionRepository()

    async def create(self, assignment_id: str, user_id: int, file: UploadFile) -> SubmissionResponseDTO:
        client = get_blob_service_client()
        # Make sure to update your settings to use azure_container_name
        container_client = client.get_container_client(settings.azure_container_name) 
        
        ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "bin"
        filename = f"submissions/{assignment_id}/{user_id}_{uuid.uuid4().hex}.{ext}"

        blob_client = container_client.get_blob_client(filename)
        content = await file.read()
        
        # Set content type for Azure
        content_settings = ContentSettings(content_type=file.content_type)
        blob_client.upload_blob(content, content_settings=content_settings, overwrite=True)

        try:
            sub = self._repo.create_with_outbox(Submission(
                user_id=user_id,
                assignment_id=assignment_id,
                filepath=filename
            ))
        except ValueError as e:
            if "Submission already exists" in e.args[0]:
                raise HTTPException(status_code=400, detail=e.args[0])

        await OutboxService().process_pending_events()
        return SubmissionResponseDTO(**sub.model_dump())

    def get_all_by_assignment(self, assignment_id: str) -> list[SubmissionResponseDTO]:
        subs = self._repo.get_all_active_submissions_by_assignment_id(assignment_id)
        return [SubmissionResponseDTO(**s.model_dump()) for s in subs]

    def get_all_by_user(self, user_id: int) -> list[SubmissionResponseDTO]:
        subs = self._repo.get_all_active_submissions_by_creator_id(user_id)
        return [SubmissionResponseDTO(**s.model_dump()) for s in subs]

    def get_file(self, sub_id: str) -> tuple[bytes, str, str]:
        sub = self._repo.get_submission_by_id(sub_id)
        if not sub:
            raise HTTPException(status_code=404, detail="Submission not found")

        client = get_blob_service_client()
        container_client = client.get_container_client(settings.azure_container_name)
        blob_client = container_client.get_blob_client(sub.filepath)
        
        if not blob_client.exists():
            raise HTTPException(status_code=404, detail="File not found in storage")

        # Read bytes and properties from Azure
        file_bytes = blob_client.download_blob().readall()
        properties = blob_client.get_blob_properties()
        content_type = properties.content_settings.content_type or "application/octet-stream"
        
        original_name = sub.filepath.split("/")[-1]
        return file_bytes, content_type, original_name

    async def update(self, sub_id: str, file: UploadFile, user_id: int) -> SubmissionResponseDTO:
        sub = self._repo.get_submission_by_id(sub_id)
        if not sub:
            raise HTTPException(status_code=404, detail="Submission not found")
        if sub.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to edit this submission")

        client = get_blob_service_client()
        container_client = client.get_container_client(settings.azure_container_name)
        
        ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "bin"
        filename = f"submissions/{sub.assignment_id}/{user_id}_{uuid.uuid4().hex}.{ext}"

        blob_client = container_client.get_blob_client(filename)
        content = await file.read()
        
        content_settings = ContentSettings(content_type=file.content_type)
        blob_client.upload_blob(content, content_settings=content_settings, overwrite=True)

        updated = self._repo.update_submission(sub_id, {"filepath": filename})
        await OutboxService().process_pending_events()
        return SubmissionResponseDTO(**updated.model_dump())

    async def delete(self, sub_id: str, user_id: int) -> None:
        sub = self._repo.get_submission_by_id(sub_id)
        if not sub:
            raise HTTPException(status_code=404, detail="Submission not found")
        if sub.user_id != user_id and user_id != -1:
            raise HTTPException(status_code=403, detail="Not authorized to delete this submission")

        self._repo.update_submission(sub_id, {"status": "deleted", "deleted_at": utcnow()})

        rating_service = RatingService()
        results = rating_service.get_by_submission(sub_id)
        # print(f"Found these results for the deleted submission id=({sub_id}):", results)
        for r in results:
            await rating_service.delete(r.id, -1)

        await OutboxService().process_pending_events()

    def get_all_submissions(self):
        submissions = self._repo.get_all_submissions()
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
