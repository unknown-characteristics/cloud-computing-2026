from fastapi import APIRouter, status, Depends, Form, File, UploadFile, Response
from app.dtos.submission_dto import SubmissionResponseDTO
from app.service.submission_service import SubmissionService
from app.helpers.user_helper import extract_user_token

router = APIRouter()
_service = SubmissionService()

@router.post("/", response_model=SubmissionResponseDTO, status_code=status.HTTP_201_CREATED)
async def create(
    assignment_id: int = Form(...),
    file: UploadFile = File(...),
    user_token: dict = Depends(extract_user_token)
):
    return await _service.create(assignment_id, user_token["sub"]["id"], file)

@router.get("/assignment/{assignment_id}", response_model=list[SubmissionResponseDTO])
async def get_by_assignment(assignment_id: int, user_token: dict = Depends(extract_user_token)):
    return _service.get_all_by_assignment(assignment_id)

@router.get("/{sub_id}/file", summary="Download submission file")
async def get_file(sub_id: int, user_token: dict = Depends(extract_user_token)):
    file_bytes, content_type, filename = _service.get_file(sub_id)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=file_bytes, media_type=content_type, headers=headers)

@router.patch("/{sub_id}", response_model=SubmissionResponseDTO)
async def update(
    sub_id: int,
    file: UploadFile = File(...),
    user_token: dict = Depends(extract_user_token)
):
    return await _service.update(sub_id, file, user_token["sub"]["id"])

@router.delete("/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(sub_id: int, user_token: dict = Depends(extract_user_token)):
    await _service.delete(sub_id, user_token["sub"]["id"])