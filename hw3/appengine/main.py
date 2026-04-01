import json
import vertexai
from vertexai.generative_models import GenerativeModel
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import pubsub_v1

from user_service.app.api.user_controller import router as user_router
from user_service.app.core.database import engine, Base
from user_service.app.model import user_model

from helpers.settings import settings

# create database
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# user endpoints 
app.include_router(user_router)

vertexai.init(
    project=settings.cloud_project_name, 
    location=settings.cloud_project_location
)

model = GenerativeModel(settings.generative_model)

class ChatRequest(BaseModel):
    message: str

@app.get("/chat")
async def chat_get(message: str):
    """Handles GET requests (e.g., from a web browser URL)"""
    if not message:
        raise HTTPException(status_code=400, detail="Please provide a 'message' parameter.")
    
    try:
        response = model.generate_content(message)
        
        # Print to App Engine logs
        print(f"User asked: {message}")
        print(f"Model replied: {response.text}")
        
        return {"response": response.text}
        
    except Exception as e:
        print(f"Error calling Vertex AI: {e}")
        raise HTTPException(status_code=500, detail="Failed to get a response from the model.")

@app.post("/chat")
async def chat_post(request: ChatRequest):
    """Handles POST requests (e.g., from an app or frontend)"""
    try:
        response = model.generate_content(request.message)
        
        # Print to App Engine logs
        print(f"User asked: {request.message}")
        print(f"Model replied: {response.text}")
        
        return {"response": response.text}
        
    except Exception as e:
        print(f"Error calling Vertex AI: {e}")
        raise HTTPException(status_code=500, detail="Failed to get a response from the model.")
    
@app.post("/pubsub")
async def send_msg(message: str):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(settings.cloud_project_name, "test-topic")
    future = publisher.publish(topic_path, bytes(json.dumps({"message": message}), "UTF-8"))    
    print(f"Future from publishing '{message}': {future}")
    return {"res": "done"}

