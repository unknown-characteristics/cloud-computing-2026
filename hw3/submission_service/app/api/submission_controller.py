from fastapi import APIRouter, status, Depends, Form, File, UploadFile, Response
from app.dtos.submission_dto import SubmissionResponseDTO
from app.service.submission_service import SubmissionService
from app.api.dependencies import get_current_user_id

router = APIRouter()
_service = SubmissionService()

@router.post("/", response_model=SubmissionResponseDTO, status_code=status.HTTP_201_CREATED)
async def create(
    assignment_id: str = Form(...),
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id)
):
    return await _service.create(assignment_id, user_id, file)

@router.get("/assignment/{assignment_id}", response_model=list[SubmissionResponseDTO])
async def get_by_assignment(assignment_id: str, user_id: int = Depends(get_current_user_id)):
    return _service.get_all_by_assignment(assignment_id)

@router.get("/{sub_id}/file", summary="Download submission file")
async def get_file(sub_id: str, user_id: int = Depends(get_current_user_id)):
    file_bytes, content_type, filename = await _service.get_file(sub_id)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=file_bytes, media_type=content_type, headers=headers)

@router.patch("/{sub_id}", response_model=SubmissionResponseDTO)
async def update(
    sub_id: str,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id)
):
    return await _service.update(sub_id, file, user_id)

@router.delete("/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(sub_id: str, user_id: int = Depends(get_current_user_id)):
    _service.delete(sub_id, user_id)