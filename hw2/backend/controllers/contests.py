from fastapi import APIRouter, HTTPException, Body, Depends, status, Response
from httpx import AsyncClient

from dtos import contests, rankings
from utils.settings import settings

from utils import auth
from utils.requests import simple_proxy_request

router = APIRouter()

async def helper_get_hint(name: str, difficulty: float, solution: str):
    # return "NONE"
    prompt = f"Question name '{name}'\nDifficulty (0 - 9) {difficulty}\nSolution '{solution}'\nGenerate a hint for the solution which does not reveal the answer while considering the difficulty. Question name may be irrelevant, focus on the solution. ONLY output the hint, and DO NOT mention the solution (or part of it) outright."
    hint_request = {"generationConfig": {"temperature": 0.3, "thinkingConfig": {"thinkingBudget": 0}}, "contents": [{"parts": [{"text": prompt}]}]}

    async with AsyncClient(timeout=30.0) as client:
        api_response = await client.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent", json = hint_request, headers = {"X-goog-api-key": settings.GEMINI_KEY})

        if api_response.status_code != 200:
            print(api_response.status_code)
            print(api_response.text)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Could not generate hint for the contest (status code {api_response.status_code}). Try again later.")

        return api_response.json()["candidates"][0]["content"]["parts"][0]["text"]


@router.get("/contests", response_model=list[contests.GetContest])
async def get_contestants(response: Response):
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contests", [200])

@router.get("/contests/{id}", response_model=contests.GetContest)
async def get_contestant_by_id(response: Response, id: int):
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contests/{id}", [200])

@router.post("/contests", response_model=contests.GetContest)
async def post_contest(response: Response, token: str = Depends(auth.oauth2_scheme), create_contest: contests.CreateContest = Body()):
    auth.check_admin_or_id_and_get_user(token, None)
    if create_contest.hint is None or create_contest.hint == "":
        create_contest.hint = await helper_get_hint(create_contest.name, create_contest.difficulty, create_contest.solution)

    return await simple_proxy_request(response, "POST", f"http://{settings.CONTREST_URL}/contests", [200], create_contest.model_dump_json(exclude_unset=True))

@router.put("/contests/{id}", response_model=contests.GetContest)
async def put_contest(response: Response, id: int, token: str = Depends(auth.oauth2_scheme), modify_contest: contests.ModifyContest = Body()):
    auth.check_admin_or_id_and_get_user(token, None)
    
    if modify_contest.hint is None or modify_contest.hint == "":
        modify_contest.hint = await helper_get_hint(modify_contest.name, modify_contest.difficulty, modify_contest.solution)

    return await simple_proxy_request(response, "PUT", f"http://{settings.CONTREST_URL}/contests/{id}", [200], modify_contest.model_dump_json())

@router.patch("/contests/{id}", response_model=contests.GetContest)
async def patch_contest(response: Response, id: int, token: str = Depends(auth.oauth2_scheme), update_contest: contests.UpdateContest = Body()):
    auth.check_admin_or_id_and_get_user(token, None)
    return await simple_proxy_request(response, "PATCH", f"http://{settings.CONTREST_URL}/contests/{id}", [200], update_contest.model_dump_json(exclude_unset=True))

@router.delete("/contests/{id}")
async def delete_contest(response: Response, id: int, token: str = Depends(auth.oauth2_scheme)):
    auth.check_admin_or_id_and_get_user(token, None)
    return await simple_proxy_request(response, "DELETE", f"http://{settings.CONTREST_URL}/contests/{id}", [200, 204])

@router.get("/contests/{id}/leaderboard", response_model=list[rankings.GetRanking])
async def get_leaderboard(response: Response, id: int):
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contests/{id}/leaderboard", [200])

@router.get("/contests/{contest_id}/leaderboard/{contestant_id}", response_model=rankings.GetRanking)
async def get_individual_ranking(response: Response, contest_id: int, contestant_id: int):
    return await simple_proxy_request(response, "GET", f"http://{settings.CONTREST_URL}/contests/{contest_id}/leaderboard/{contestant_id}", [200])
