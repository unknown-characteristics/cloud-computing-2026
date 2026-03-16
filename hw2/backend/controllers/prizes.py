from fastapi import APIRouter, HTTPException, Body, Depends, status, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from httpx import AsyncClient
from pydantic.type_adapter import TypeAdapter

from dtos import users, contests, prizes
from models.user import User
from enums.status import StatusEnum
from utils.database import get_db
from utils.settings import settings

from utils import auth
from utils.requests import simple_proxy_request, simple_request

import json
from urllib.parse import urlencode


router = APIRouter()

async def helper_get_photo(description: str):
    async with AsyncClient() as client:
        url = f"https://api.unsplash.com/search/photos?{urlencode({"query": description})}"
        api_response = await client.get(url, headers={"Authorization": f"Client-ID {settings.UNSPLASH_KEY}"})

        if api_response.status_code != 200:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Couldn't fetch photos (status code {api_response.status_code}). Please try again later")
        
        photos = api_response.json()
        if photos["total"] == 0:
            return None
        
        best_photo = photos["results"][0]

        photo_model = prizes.PhotoModel(
            author_name = best_photo["user"]["name"],
            author_url = best_photo["user"]["links"]["html"],
            photo_url = best_photo["urls"]["regular"],
            photo_page_url = best_photo["links"]["html"]
        )

        return photo_model


@router.get("/contests/{contest_id}/prizes", response_model=list[prizes.GetPrize])
async def get_prizes(contest_id: int, response: Response):
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contests/{contest_id}/prizes", [200])

@router.get("/contests/{contest_id}/prizes/{prize_id}", response_model=prizes.GetPrize)
async def get_prize_by_id(contest_id: int, prize_id: int, response: Response):
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contests/{contest_id}/prizes/{prize_id}", [200])

@router.post("/contests/{contest_id}/prizes", response_model=prizes.GetPrize)
async def post_prize(response: Response, contest_id: int, token: str = Depends(auth.oauth2_scheme), create_prize: prizes.CreatePrize = Body()):
    auth.check_admin_or_id_and_get_user(token, None)
    if create_prize.photo_data is None:
        create_prize.photo_data = await helper_get_photo(create_prize.description)
    return await simple_proxy_request(response, "POST", f"http://{settings.CONTREST_URL}/contests/{contest_id}/prizes", [200, 201], create_prize.model_dump_json())

@router.put("/contests/{contest_id}/prizes/{prize_id}", response_model=prizes.GetPrize)
async def put_prize(response: Response, contest_id: int, prize_id: int, token: str = Depends(auth.oauth2_scheme), modify_prize: prizes.ModifyPrize = Body()):
    auth.check_admin_or_id_and_get_user(token, None)
    if modify_prize.photo_data is None:
        modify_prize.photo_data = await helper_get_photo(modify_prize.description)
    return await simple_proxy_request(response, "PUT", f"http://{settings.CONTREST_URL}/contests/{contest_id}/prizes/{prize_id}", [200], modify_prize.model_dump_json())

@router.patch("/contests/{contest_id}/prizes/{prize_id}", response_model=prizes.GetPrize)
async def patch_prize(response: Response, contest_id: int, prize_id: int, token: str = Depends(auth.oauth2_scheme), update_prize: prizes.UpdatePrize = Body()):
    auth.check_admin_or_id_and_get_user(token, None)
    if update_prize.photo_data is None and update_prize.description != None:
        update_prize.photo_data = await helper_get_photo(update_prize.description)
    return await simple_proxy_request(response, "PATCH", f"http://{settings.CONTREST_URL}/contests/{contest_id}/prizes/{prize_id}", [200], update_prize.model_dump_json(exclude_unset=True))

@router.delete("/contests/{contest_id}/prizes/{prize_id}")
async def delete_prize(response: Response, contest_id: int, prize_id: int, token: str = Depends(auth.oauth2_scheme)):
    auth.check_admin_or_id_and_get_user(token, None)
    return await simple_proxy_request(response, "DELETE", f"http://{settings.CONTREST_URL}/contests/{contest_id}/prizes/{prize_id}", [200, 204])
