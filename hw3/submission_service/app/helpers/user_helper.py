from fastapi import Request
import base64, json

def extract_user_token(request: Request):
    user_data = request.headers.get("X-User-Token")
    if user_data is None:
        return None
    
    json_data = base64.b64decode(user_data)
    return json.loads(json_data)
