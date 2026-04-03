import os
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from google.cloud import secretmanager, run_v2
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token
import json
import base64

app = FastAPI(title="API Gateway")

# --- SETARI CORS ---
# Acest bloc permite frontend-ului tău (chiar și de pe localhost) să comunice cu Gateway-ul
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite orice domeniu
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, PATCH, etc.
    allow_headers=["*"],
)

# Configuration
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

# Global cache for the Public Key string
_public_key_cache = None


def get_cloud_run_service_url(service_name: str, region: str = "europe-west1"):
    """Programmatically retrieves the URL of a Cloud Run service."""
    client = run_v2.ServicesClient()
    parent = f"projects/{PROJECT_ID}/locations/{region}/services/{service_name}"
    try:
        service = client.get_service(name=parent)
        return service.uri
    except Exception as e:
        print(f"Error fetching service URL for {service_name}: {e}")
        return None


# Cautam URL-urile tuturor microserviciilor (numele trebuie sa coincida cu cele din Cloud Run)
USERS_SERVICE_URL = get_cloud_run_service_url("users-service", "europe-west1")
ASSIGNMENTS_SERVICE_URL = get_cloud_run_service_url("assignments-service", "europe-west1")
SUBMISSIONS_SERVICE_URL = get_cloud_run_service_url("submissions-service", "europe-west1")
RATINGS_SERVICE_URL = get_cloud_run_service_url("submissions-service", "europe-west1")


def get_secret_payload(secret_id: str, version_id: str = "latest"):
    """Fetches a secret from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


async def get_public_key():
    """Retrieves and caches the RSA Public Key from Secret Manager."""
    global _public_key_cache
    if _public_key_cache is None:
        _public_key_cache = get_secret_payload("USERS_JWT_KEY_PUBLIC")
    return _public_key_cache


async def validate_user_jwt_optional(request: Request):
    """Verifica token-ul JWT, dar daca nu exista nu da eroare (pentru rute publice)"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    public_key = await get_public_key()
    try:
        decoded_payload = jwt.decode(
            token, public_key, algorithms=["RS256"], audience=PROJECT_ID, issuer=USERS_SERVICE_URL
        )
        return decoded_payload
    except Exception:
        return None


async def validate_user_jwt_required(request: Request):
    """Verifica token-ul JWT si DA eroare daca nu e valid (pentru rute protejate)"""
    user = await validate_user_jwt_optional(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def proxy_request(request: Request, path: str, service_url: str, user: dict | None):
    if not service_url:
        raise HTTPException(status_code=503, detail="Service not available")

    # 1. Get Google OIDC token for Cloud Run IAM
    auth_req = GoogleAuthRequest()
    google_token = id_token.fetch_id_token(auth_req, service_url)

    # 2. Proxy request
    backend_url = f"{service_url}/{path}"
    forbidden = {"authorization", "host", "content-length", "connection"}
    headers = {k: v for k, v in request.headers.items() if k.lower() not in forbidden}

    headers["Authorization"] = f"Bearer {google_token}"
    if user != None:
        headers["X-User-Token"] = base64.b64encode(json.dumps(user).encode("utf-8")).decode("utf-8")

    async with httpx.AsyncClient() as client:
        proxy_resp = await client.request(
            method=request.method,
            url=backend_url,
            headers=headers,
            content=await request.body(),
            params=request.query_params,
            timeout=15.0
        )

    excluded_headers = {"content-length", "content-encoding", "transfer-encoding", "connection"}
    return Response(
        content=proxy_resp.content,
        status_code=proxy_resp.status_code,
        headers={key: value for key, value in proxy_resp.headers.items() if key.lower() not in excluded_headers},
        media_type=proxy_resp.headers.get("content-type")
    )


# --- RUTELE (PROXY) PENTRU MICROSERVICII ---

@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def users_proxy(request: Request, path: str, user: dict | None = Depends(validate_user_jwt_optional)):
    # Adaugam /users/ inapoi in ruta
    return await proxy_request(request, f"/users/{path}", USERS_SERVICE_URL, user)

@app.api_route("/api/assignments/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def assignments_proxy(request: Request, path: str, user: dict | None = Depends(validate_user_jwt_optional)):
    # Adaugam /assignments/ inapoi in ruta exact cum asteapta microserviciul
    return await proxy_request(request, f"/assignments/{path}", ASSIGNMENTS_SERVICE_URL, user)

@app.api_route("/api/submissions/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def submissions_proxy(request: Request, path: str, user: dict | None = Depends(validate_user_jwt_optional)):
    # Presupunand ca si submission_service foloseste prefix="/submissions" in main.py
    return await proxy_request(request, f"/submissions/{path}", SUBMISSIONS_SERVICE_URL, user)

@app.api_route("/api/ratings/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def ratings_proxy(request: Request, path: str, user: dict | None = Depends(validate_user_jwt_optional)):
    return await proxy_request(request, f"/ratings/{path}", RATINGS_SERVICE_URL, user)

app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

# Catch-all route to serve React index.html
@app.get("/{full_path:path}")
def serve_react(full_path: str):
    file_path = os.path.join("dist", full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        return FileResponse("dist/index.html")
