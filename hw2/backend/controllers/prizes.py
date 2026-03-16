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

def helper_convert_photo_to_model(photo: dict):
    return prizes.GetPhotoModel(
            author_name = photo["user"]["name"],
            author_url = photo["user"]["links"]["html"],
            photo_url = photo["urls"]["regular"],
            photo_page_url = photo["links"]["html"],
            download_location = photo["links"]["download_location"]
        )

async def helper_get_photos(description: str):
    async with AsyncClient() as client:
        url = f"https://api.unsplash.com/search/photos?{urlencode({"query": description})}"
        api_response = await client.get(url, headers={"Authorization": f"Client-ID {settings.UNSPLASH_KEY}"})

        if api_response.status_code != 200:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Couldn't fetch photos (status code {api_response.status_code}). Please try again later")
        return [helper_convert_photo_to_model(photo) for photo in api_response.json()["results"]]

async def helper_trigger_photo_download(download_location: str):
    async with AsyncClient() as client:
        await client.get(download_location, headers={"Authorization": f"Client-ID {settings.UNSPLASH_KEY}"})

@router.get("/contests/{contest_id}/prizes", response_model=list[prizes.GetPrize])
async def get_prizes(contest_id: int, response: Response):
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contests/{contest_id}/prizes", [200])

@router.get("/contests/{contest_id}/prizes/{prize_id}", response_model=prizes.GetPrize)
async def get_prize_by_id(contest_id: int, prize_id: int, response: Response):
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contests/{contest_id}/prizes/{prize_id}", [200])

@router.post("/contests/{contest_id}/prizes", response_model=prizes.GetPrize)
async def post_prize(response: Response, contest_id: int, token: str = Depends(auth.oauth2_scheme), create_prize: prizes.CreatePrize = Body()):
    auth.check_admin_or_id_and_get_user(token, None)
    if create_prize.photo_data != None:
        await helper_trigger_photo_download(create_prize.photo_data.download_location)
        save_photo_model = prizes.SavePhotoModel.model_validate(create_prize.photo_data.model_dump())
        create_prize.photo_data = save_photo_model
    return await simple_proxy_request(response, "POST", f"http://{settings.CONTREST_URL}/contests/{contest_id}/prizes", [200, 201], create_prize.model_dump_json())

@router.put("/contests/{contest_id}/prizes/{prize_id}", response_model=prizes.GetPrize)
async def put_prize(response: Response, contest_id: int, prize_id: int, token: str = Depends(auth.oauth2_scheme), modify_prize: prizes.ModifyPrize = Body()):
    auth.check_admin_or_id_and_get_user(token, None)
    if modify_prize.photo_data != None:
        await helper_trigger_photo_download(modify_prize.photo_data.download_location)
        save_photo_model = prizes.SavePhotoModel.model_validate(modify_prize.photo_data.model_dump())
        modify_prize.photo_data = save_photo_model
    return await simple_proxy_request(response, "PUT", f"http://{settings.CONTREST_URL}/contests/{contest_id}/prizes/{prize_id}", [200], modify_prize.model_dump_json())

@router.patch("/contests/{contest_id}/prizes/{prize_id}", response_model=prizes.GetPrize)
async def patch_prize(response: Response, contest_id: int, prize_id: int, token: str = Depends(auth.oauth2_scheme), update_prize: prizes.UpdatePrize = Body()):
    auth.check_admin_or_id_and_get_user(token, None)
    if update_prize.photo_data != None:
        await helper_trigger_photo_download(update_prize.photo_data.download_location)
        save_photo_model = prizes.SavePhotoModel.model_validate(update_prize.photo_data.model_dump())
        update_prize.photo_data = save_photo_model
    return await simple_proxy_request(response, "PATCH", f"http://{settings.CONTREST_URL}/contests/{contest_id}/prizes/{prize_id}", [200], update_prize.model_dump_json(exclude_unset=True))

@router.delete("/contests/{contest_id}/prizes/{prize_id}")
async def delete_prize(response: Response, contest_id: int, prize_id: int, token: str = Depends(auth.oauth2_scheme)):
    auth.check_admin_or_id_and_get_user(token, None)
    return await simple_proxy_request(response, "DELETE", f"http://{settings.CONTREST_URL}/contests/{contest_id}/prizes/{prize_id}", [200, 204])

@router.get("/search-prize-photos", response_model=list[prizes.GetPhotoModel])
async def get_photos(description: str, token: str = Depends(auth.oauth2_scheme)):
    auth.check_admin_or_id_and_get_user(token, None)
    return await helper_get_photos(description)
