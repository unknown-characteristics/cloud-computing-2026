from fastapi import APIRouter, status, Depends, Form, File, UploadFile, Response
from app.dtos.submission_dto import SubmissionResponseDTO
from app.service.submission_service import SubmissionService
from app.helpers.user_helper import extract_user_token
import json

router = APIRouter()
_service = SubmissionService()

# Funcție sigură pentru a extrage ID-ul
def get_id(token: dict):
    sub = token.get("sub", "{}")
    if isinstance(sub, str):
        return int(json.loads(sub).get("id"))
    return int(sub.get("id"))

@router.post("/", response_model=SubmissionResponseDTO, status_code=status.HTTP_201_CREATED)
async def create(
    assignment_id: str = Form(...),
    file: UploadFile = File(...),
    user_token: dict = Depends(extract_user_token)
):
    return await _service.create(assignment_id, get_id(user_token), file)

@router.get("/assignment/{assignment_id}", response_model=list[SubmissionResponseDTO])
async def get_by_assignment(assignment_id: str, user_token: dict = Depends(extract_user_token)):
    return _service.get_all_by_assignment(assignment_id)

@router.get("/{sub_id}/file", summary="Download submission file")
async def get_file(sub_id: str, user_token: dict = Depends(extract_user_token)):
    file_bytes, content_type, filename = _service.get_file(sub_id)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=file_bytes, media_type=content_type, headers=headers)

@router.patch("/{sub_id}", response_model=SubmissionResponseDTO)
async def update(
    sub_id: str,
    file: UploadFile = File(...),
    user_token: dict = Depends(extract_user_token)
):
    return await _service.update(sub_id, file, get_id(user_token))

@router.get("/", response_model=list[SubmissionResponseDTO])
async def get_all_submissions(user_token: dict = Depends(extract_user_token)):
    return _service.get_all_submissions()

@router.delete("/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(sub_id: str, user_token: dict = Depends(extract_user_token)):
    await _service.delete(sub_id, user_token["sub"]["id"])
