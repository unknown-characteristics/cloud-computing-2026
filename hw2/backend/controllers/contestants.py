from fastapi import APIRouter, Body, Depends, Response

from dtos import contestants
from utils.settings import settings

from utils import auth
from utils.requests import simple_proxy_request

router = APIRouter()

@router.get("/contestants/me", response_model=contestants.GetContestant)
async def get_current_contestant(response: Response, token: str = Depends(auth.oauth2_scheme)):
    payload = auth.decode_token(token)
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contestants/{payload["contestant_id"]}", [200])

@router.get("/contestants", response_model=list[contestants.GetContestant])
async def get_contestants(response: Response, token: str = Depends(auth.oauth2_scheme)):
    auth.check_admin_or_id_and_get_user(token, None)
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contestants", [200])

@router.get("/contestants/{id}", response_model=contestants.GetContestant)
async def get_contestant_by_id(response: Response, id: int, token: str = Depends(auth.oauth2_scheme)):
    auth.check_admin_or_id_and_get_user(token, None, id, True)
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contestants/{id}", [200])

@router.put("/contestants/{id}", response_model=contestants.GetContestant)
async def put_contestant(response: Response, id: int, token: str = Depends(auth.oauth2_scheme), modify_contestant: contestants.ModifyContestant = Body()):
    auth.check_admin_or_id_and_get_user(token, None, id, True)
    return await simple_proxy_request(response, "PUT", f"http://{settings.CONTREST_URL}/contestants/{id}", [200], modify_contestant.model_dump_json())

@router.patch("/contestants/{id}", response_model=contestants.GetContestant)
async def patch_contestant(response: Response, id: int, token: str = Depends(auth.oauth2_scheme), update_contestant: contestants.UpdateContestant = Body()):
    auth.check_admin_or_id_and_get_user(token, None, id, True)
    return await simple_proxy_request(response, "PATCH", f"http://{settings.CONTREST_URL}/contestants/{id}", [200], update_contestant.model_dump_json(exclude_unset=True))
