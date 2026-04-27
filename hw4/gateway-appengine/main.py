"""
API Gateway — Azure version.

Two layers of auth on every proxied request:

1. PLATFORM auth (replaces GCP IAM / `--no-allow-unauthenticated`):
   The gateway's Managed Identity acquires an Entra ID access token whose
   audience is the downstream microservice's App Registration. The gateway
   sends it as `Authorization: Bearer <token>`. Each microservice has Easy
   Auth ("Authentication" blade in the portal) configured to require that
   audience, so unauthenticated requests are rejected before reaching the
   app code.

2. END-USER auth (unchanged in spirit from the GCP version):
   The user's RS256 JWT (issued by users-service) is validated here against
   a public key stored in Key Vault, and the user's claims are forwarded to
   the downstream service in `X-User-Token` (base64-encoded JSON).
"""
import base64
import json
import os
from functools import lru_cache
from typing import Optional

import httpx
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from jose import jwt


# ---------------------------------------------------------------------------
# Configuration (read from App Service Application settings)
# ---------------------------------------------------------------------------
KEY_VAULT_URL = os.environ.get("KEY_VAULT_URL", "")
USERS_PUBLIC_KEY_SECRET = os.environ.get(
    "USERS_PUBLIC_KEY_SECRET", "USERS-JWT-KEY-PUBLIC"
)
JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE", "comparena-users")
JWT_ISSUER = os.environ.get("JWT_ISSUER", "users-service")  # optional; if set, enforced

# One pair (URL, audience) per downstream service.
# - URL is the App Service base URL, e.g. https://users-service.azurewebsites.net
# - AUDIENCE is the App ID URI of that service's Entra App Registration
#   (e.g. api://<guid>) — the gateway requests a token with this scope and the
#   downstream Easy Auth validates it.
SERVICES = {
    "users": (
        os.environ.get("USERS_SERVICE_URL", ""),
        os.environ.get("USERS_SERVICE_AUDIENCE", ""),
    ),
    "assignments": (
        os.environ.get("ASSIGNMENTS_SERVICE_URL", ""),
        os.environ.get("ASSIGNMENTS_SERVICE_AUDIENCE", ""),
    ),
    "submissions": (
        os.environ.get("SUBMISSIONS_SERVICE_URL", ""),
        os.environ.get("SUBMISSIONS_SERVICE_AUDIENCE", ""),
    ),
    # Ratings live inside submission_service in this codebase
    "ratings": (
        os.environ.get("SUBMISSIONS_SERVICE_URL", ""),
        os.environ.get("SUBMISSIONS_SERVICE_AUDIENCE", ""),
    ),
}


# ---------------------------------------------------------------------------
# Azure clients
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _credential() -> DefaultAzureCredential:
    """Picks Managed Identity in App Service, `az login` locally."""
    return DefaultAzureCredential()


@lru_cache(maxsize=1)
def _kv_client() -> SecretClient:
    if not KEY_VAULT_URL:
        raise RuntimeError("KEY_VAULT_URL not configured")
    return SecretClient(vault_url=KEY_VAULT_URL, credential=_credential())


@lru_cache(maxsize=1)
def _user_jwt_public_key() -> str:
    """Public key used to validate end-user JWTs. Cached for the process
    lifetime — restart the app to pick up rotation."""
    return _kv_client().get_secret(USERS_PUBLIC_KEY_SECRET).value


def _azure_token_for(audience: str) -> str:
    """Get an Entra ID access token for a downstream service.

    The azure-identity SDK already caches and refreshes tokens internally, so
    calling this on every request is cheap (a cache hit until ~5 min before
    expiry, then a single refresh).
    """
    return _credential().get_token(f"{audience}/.default").token


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}


# ---------------------------------------------------------------------------
# End-user JWT validation
# ---------------------------------------------------------------------------
async def validate_user_jwt_optional(request: Request) -> Optional[dict]:
    """Return decoded user claims if a valid bearer token is present, else None."""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]

    try:
        return jwt.decode(
            token,
            _user_jwt_public_key(),
            algorithms=["RS256"],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER if JWT_ISSUER else None,
            options={"verify_iss": bool(JWT_ISSUER)},
        )
    except Exception as exc:
        # Don't leak details to the client.
        print(f"[gateway] user JWT rejected: {exc}")
        return None


async def validate_user_jwt_required(request: Request) -> dict:
    user = await validate_user_jwt_optional(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


# ---------------------------------------------------------------------------
# Proxy core
# ---------------------------------------------------------------------------
_HOP_BY_HOP_HEADERS = {
    "authorization",          # we replace it with our own Azure token
    "host",                   # httpx sets the right one for the target
    "content-length",         # httpx recomputes
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


async def _proxy(
    request: Request,
    service_key: str,
    downstream_path: str,
    user: Optional[dict],
) -> Response:
    service_url, service_audience = SERVICES.get(service_key, ("", ""))
    if not service_url or not service_audience:
        raise HTTPException(
            status_code=503,
            detail=f"service '{service_key}' not configured",
        )

    target = f"{service_url.rstrip('/')}/{downstream_path.lstrip('/')}"

    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP_HEADERS
    }
    headers["Authorization"] = f"Bearer {_azure_token_for(service_audience)}"
    if user is not None:
        headers["X-User-Token"] = base64.b64encode(
            json.dumps(user).encode("utf-8")
        ).decode("utf-8")

    body = await request.body()

    async with httpx.AsyncClient(timeout=30.0) as client:
        upstream = await client.request(
            method=request.method,
            url=target,
            headers=headers,
            content=body,
            params=request.query_params,
        )

    excluded = {"content-length", "content-encoding", "transfer-encoding", "connection"}
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers={
            k: v for k, v in upstream.headers.items() if k.lower() not in excluded
        },
        media_type=upstream.headers.get("content-type"),
    )


# ---------------------------------------------------------------------------
# Routes — one block per microservice. The path the user hits is rewritten to
# match what the downstream FastAPI app expects (the same prefix it uses
# internally, e.g. /users, /assignments, /submissions, /ratings).
# ---------------------------------------------------------------------------
_PROXY_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]


@app.api_route("/api/users/{path:path}", methods=_PROXY_METHODS)
async def users_proxy(
    request: Request,
    path: str,
    user: Optional[dict] = Depends(validate_user_jwt_optional),
):
    return await _proxy(request, "users", f"/users/{path}", user)


@app.api_route("/api/assignments/{path:path}", methods=_PROXY_METHODS)
async def assignments_proxy(
    request: Request,
    path: str,
    user: Optional[dict] = Depends(validate_user_jwt_optional),
):
    return await _proxy(request, "assignments", f"/assignments/{path}", user)


@app.api_route("/api/submissions/{path:path}", methods=_PROXY_METHODS)
async def submissions_proxy(
    request: Request,
    path: str,
    user: Optional[dict] = Depends(validate_user_jwt_optional),
):
    return await _proxy(request, "submissions", f"/submissions/{path}", user)


@app.api_route("/api/ratings/{path:path}", methods=_PROXY_METHODS)
async def ratings_proxy(
    request: Request,
    path: str,
    user: Optional[dict] = Depends(validate_user_jwt_optional),
):
    return await _proxy(request, "ratings", f"/ratings/{path}", user)


# ---------------------------------------------------------------------------
# Static frontend (must be mounted AFTER the /api routes so it doesn't
# swallow them)
# ---------------------------------------------------------------------------
DIST_DIR = os.path.join(os.path.dirname(__file__), "dist")
ASSETS_DIR = os.path.join(DIST_DIR, "assets")

if os.path.isdir(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/{full_path:path}")
def serve_react(full_path: str):
    candidate = os.path.join(DIST_DIR, full_path)
    if full_path and os.path.isfile(candidate):
        return FileResponse(candidate)
    return FileResponse(os.path.join(DIST_DIR, "index.html"))
