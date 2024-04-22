import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uuid

from app.ui_gen import ui_gen, TuiGenResponse
from run import call_gpt
from llm import OpenAiModel, OpenAiChatModels
from MASProd.main import chat_serve
from rich.console import Console


# Load the environment variables
load_dotenv()
console = Console()

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


@app.post("/gpt/chat")
async def tui_chat(request: Request):
    # get the prompt from the request body
    try:
        req_body = await request.json()
        text = req_body["text"]
    except:
        print("Invalid request", request)
        raise HTTPException(status_code=400, detail="Invalid Request body")

    chat_response_from_mas = await chat_serve(user_prompt=text)
    console.log(f"[green]INFO: [/green]     MAS response generated successfully!")
    r_uuid = uuid.uuid4()
    formatted_chat = f"""User: {text}
    Assistant: {chat_response_from_mas}"""
    tui_gen_response: TuiGenResponse = ui_gen(
        r_uuid, formatted_chat, multiprocessing=True
    )
    return {
        "chat_response": chat_response_from_mas,
        "tui_gen_response": tui_gen_response,
    }


# NOTE: Every time you want to restart the chat, change the index variable to 1 in the script.json file
@app.post("/tui/chat")
async def gpt_chat(request: Request):
    try:
        req_body = await request.json()
        text = req_body["text"]
        print(text)
    except:
        print("Invalid request", request)
        raise HTTPException(status_code=400, detail="Invalid Request body")

    with open("script.json", "r") as f:
        script = json.load(f)
    messages = script["messages"]
    idx = script["idx"]

    assistant_response = messages[idx].split("Bot: ")[1]
    idx += 2

    r_uuid = uuid.uuid4()
    tui_gen_response = ui_gen(
        uuid.uuid4(),
        f"User: {text}\nAssistant: {assistant_response}",
        console,
        True,
        True,
    )

    # write the updated index back to the file
    with open("script.json", "w") as f:
        json.dump({"messages": messages, "idx": idx}, f)

    return {"chat_response": assistant_response, "tui_gen_response": tui_gen_response}


# Run the server
# uvicorn server:app --reload
