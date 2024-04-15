import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uuid

from app.ui_gen import ui_gen
from run import call_gpt
from llm import OpenAiModel, OpenAiChatModels


# Load the environment variables
load_dotenv()

# Create the FastAPI app
app = FastAPI()
# Add the CORS middleware
# NOTE: This is only for development purposes. In production, you should specify the allowed origins.
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/gpt/")
async def gpt(request: Request):
    # get the prompt from the request body
    try:
        req_body = await request.json()
        text = req_body["text"]
    except:
        print("Invalid request", request)
        raise HTTPException(status_code=400, detail="Invalid Request body")

    return {"response": call_gpt(prompt=text, system_message_path="./prompts/main.md", response_format={"type": "json_object"})}


@app.post("/tui/gen")
async def tui_gen(request: Request):
    # get the prompt from the request body
    try:
        req_body = await request.json()
        text = req_body["text"]
    except:
        print("Invalid request", request)
        raise HTTPException(status_code=400, detail="Invalid Request body")

    r_uuid = uuid.uuid4()

    return ui_gen(r_uuid, text)

# Run the server
# uvicorn local_fast_gpt:app --reload
