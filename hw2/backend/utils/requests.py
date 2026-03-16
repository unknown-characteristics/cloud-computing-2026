from httpx import AsyncClient, Response
from fastapi.responses import PlainTextResponse

async def simple_request(method, url, body_json = None) -> Response:
    async with AsyncClient() as client:
        request = client.build_request(method, url, content=body_json)
        return await client.send(request)

def convert_response(response) -> PlainTextResponse:
    return PlainTextResponse(response.text, media_type="application/json", status_code=response.status_code)

async def simple_proxy_request(response: Response, method: str, url: str, ok_statuses: list[int], body_json: str = None):
    api_response = await simple_request(method, url, body_json)
    response.status_code = api_response.status_code
    if response.status_code in ok_statuses:
        return api_response.json() if api_response.text != "" else PlainTextResponse("", response.status_code)
    else:
        return PlainTextResponse(api_response.text, media_type="application/json", status_code=api_response.status_code)
