import base64
import json
from fastapi import Request, HTTPException, status

def get_current_user_id(request: Request) -> int:
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Missing X-User-Token header."
        )
    try:
        decoded = base64.b64decode(token).decode("utf-8")
        user_data = json.loads(decoded)
        return int(user_data.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth token format."
        )