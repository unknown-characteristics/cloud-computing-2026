from google.oauth2 import id_token
from google.auth.transport import requests
from flask import Request
from pydantic import BaseModel
import base64
import functions_framework
from google.cloud import storage, datastore
import datetime

class TestTopic(BaseModel):
    message: str

class PushRequest(BaseModel):
    message: dict
    subscription: str
    deliveryAttempt: int | None = None

    class Config:
        extra = "allow"

@functions_framework.http
def my_function(request: Request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return "Unauthorized", 401

    token = auth_header.split(" ")[1]

    try:
        # validate jwt
        decoded_token = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience="https://test-function-1088240463128.europe-west1.run.app"
        )

        if decoded_token["iss"] not in [
            "https://accounts.google.com",
            "accounts.google.com"
        ]:
            return "Invalid issuer", 401

    except Exception as e:
        return f"Unauthorized: {str(e)}", 401

    # jwt validated
    
    data = PushRequest.model_validate(request.json)
    obj = base64.b64decode(data.message["data"]).decode("utf-8")

    try:
        obj = TestTopic.model_validate_json(obj)
    except Exception as e:
        return f"Bad format: {str(e)}", 401
    
    now = datetime.datetime.now(datetime.timezone.utc)
    # storage bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket("asg-data67")
    blob = bucket.blob("test-" + now.strftime("%Y-%m-%d_%H-%M-%S_%z"))

    blob.upload_from_string(obj.message)

    # datastore database
    datastore_client = datastore.Client(namespace="test", database="cloud-hw1")
    kind = "kind-test-2"
    key = datastore_client.key(kind)
    entity = datastore.Entity(key)
    entity.update({
        "message": obj.message,
        "date": now
    })
    datastore_client.put(entity)

    return f"Uploaded '{obj.message}'"
