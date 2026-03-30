import json
import vertexai
from vertexai.generative_models import GenerativeModel
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import pubsub_v1

# Initialize FastAPI app
app = FastAPI()

vertexai.init(project="cloudcomputing-491711", location="us-central1")

model = GenerativeModel("gemini-2.5-flash")

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
    topic_path = publisher.topic_path("cloudcomputing-491711", "test-topic")
    future = publisher.publish(topic_path, bytes(json.dumps({"message": message}), "UTF-8"))    
    print(f"Future from publishing '{message}': {future}")
    return {"res": "done"}

