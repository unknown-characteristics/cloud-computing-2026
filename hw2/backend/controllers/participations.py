from fastapi import APIRouter, HTTPException, Body, Depends, status, Response
from httpx import AsyncClient

from dtos import contests, participations
from enums.status import StatusEnum
from enums.role import RoleEnum
from utils.settings import settings

from utils import auth
from utils.requests import simple_proxy_request, simple_request

router = APIRouter()

async def helper_score_answer(contest_id: int, answer: str):
    contest_response = await simple_request("GET", f"http://{settings.CONTREST_URL}/contests/{contest_id}")
    contest = contests.GetContest.model_validate_json(contest_response.text)

    if contest.status == StatusEnum.ended:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cannot join/submit contest after contest has ended")

    compare_request = {"text_1": answer, "text_2": contest.solution}
    async with AsyncClient(timeout=30.0) as client:
        api_response = await client.post("https://api.api-ninjas.com/v1/textsimilarity", json = compare_request, headers = {"X-Api-Key": settings.NINJAS_KEY})

        if api_response.status_code != 200:
            print(api_response.status_code)
            print(api_response.text)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Could not compare answer to solution (status code {api_response.status_code}). Try again later.")

        return api_response.json()["similarity"]

@router.get("/contests/{contest_id}/participations", response_model=list[participations.GetParticipation])
async def get_participations_by_contest_id(contest_id: int, response: Response, token: str = Depends(auth.oauth2_scheme)):
    auth.check_admin_or_id_and_get_user(token, None)
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contests/{contest_id}/participations", [200])

@router.get("/contestants/{contestant_id}/participations", response_model=list[participations.GetParticipation])
async def get_participations_by_contestant_id(contestant_id: int, response: Response, token: str = Depends(auth.oauth2_scheme)):
    auth.check_admin_or_id_and_get_user(token, None, contestant_id, True)
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contestants/{contestant_id}/participations", [200])

@router.get("/contestants/{contestant_id}/participations/{contest_id}", response_model=participations.GetParticipation)
@router.get("/contests/{contest_id}/participations/{contestant_id}", response_model=participations.GetParticipation)
async def get_individual_participation(contest_id: int, contestant_id: int, response: Response, token: str = Depends(auth.oauth2_scheme)):
    auth.check_admin_or_id_and_get_user(token, None, contestant_id, True)
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contests/{contest_id}/participations/{contestant_id}", [200])

@router.post("/contests/{contest_id}/participations", response_model=participations.GetParticipation)
@router.post("/contestants/{contestant_id}/participations", response_model=participations.GetParticipation)
async def post_participation(response: Response, contest_id: int = -1, contestant_id: int = -1, token: str = Depends(auth.oauth2_scheme), create_participation: participations.CreateParticipation = Body()):
    if contestant_id == -1:
        contestant_id = create_participation.contestant_id
    if contest_id == -1:
        contest_id = create_participation.contest_id
    
    auth.check_admin_or_id_and_get_user(token, None, contestant_id, True)

    if create_participation.score is None or auth.decode_token(token)["role"] != RoleEnum.admin.value:
        if create_participation.answer is None:
            create_participation.score = 0
        else:
            create_participation.score = await helper_score_answer(contest_id, create_participation.answer)

    return await simple_proxy_request(response, "POST", f"http://{settings.CONTREST_URL}/contests/{contest_id}/participations", [200, 201], create_participation.model_dump_json())

@router.put("/contests/{contest_id}/participations/{contestant_id}", response_model=participations.GetParticipation)
@router.put("/contestants/{contestant_id}/participations/{contest_id}", response_model=participations.GetParticipation)
async def put_participation(response: Response, contest_id: int, contestant_id: int, token: str = Depends(auth.oauth2_scheme), modify_participation: participations.ModifyParticipation = Body()):
    auth.check_admin_or_id_and_get_user(token, None, contestant_id, True)

    if modify_participation.score is None or auth.decode_token(token)["role"] != RoleEnum.admin.value:
        if modify_participation.answer is None:
            modify_participation.score = 0
        else:
            modify_participation.score = await helper_score_answer(contest_id, modify_participation.answer)

    return await simple_proxy_request(response, "PUT", f"http://{settings.CONTREST_URL}/contests/{contest_id}/participations/{contestant_id}", [200], modify_participation.model_dump_json())

@router.patch("/contests/{contest_id}/participations/{contestant_id}", response_model=participations.GetParticipation)
@router.patch("/contestants/{contestant_id}/participations/{contest_id}", response_model=participations.GetParticipation)
async def patch_participation(response: Response, contest_id: int, contestant_id: int, token: str = Depends(auth.oauth2_scheme), update_participation: participations.UpdateParticipation = Body()):
    auth.check_admin_or_id_and_get_user(token, None, contestant_id, True)

    if update_participation.score is None or auth.decode_token(token)["role"] != RoleEnum.admin.value:
        if update_participation.answer is None:
            update_participation.score = 0
        else:
            update_participation.score = await helper_score_answer(contest_id, update_participation.answer)

    return await simple_proxy_request(response, "PATCH", f"http://{settings.CONTREST_URL}/contests/{contest_id}/participations/{contestant_id}", [200], update_participation.model_dump_json(exclude_unset=True))

@router.delete("/contests/{contest_id}/participations/{contestant_id}")
@router.delete("/contestants/{contestant_id}/participations/{contest_id}")
async def delete_participation(response: Response, contest_id: int, contestant_id: int, token: str = Depends(auth.oauth2_scheme)):
    auth.check_admin_or_id_and_get_user(token, None, contestant_id, True)
    return await simple_proxy_request(response, "DELETE", f"http://{settings.CONTREST_URL}/contests/{contest_id}/participations/{contestant_id}", [200, 204])
