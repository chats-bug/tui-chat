import json
import os
from dataclasses import dataclass
from uuid import UUID

from dotenv import load_dotenv
from rich.console import Console

from app.response_types import MainResponse, HTMLResponse, CSSResponse, JSResponse
from llm import OpenAIDecodingArguments, OpenAiModel, OpenAiChatModels


load_dotenv()
console = Console()


# Initialize the OpenAI model
model = OpenAiModel(
    model=OpenAiChatModels.GPT_4_TURBO,
    api_key=os.getenv("OPENAI_API_KEY"),
)


@dataclass
class TuiGenResponse:
    uuid: UUID
    main_response: MainResponse
    html_response: str
    css_response: str
    js_response: str


def ui_gen(r_uuid: UUID, text: str, console: Console = console, log_to_console: bool = False) -> TuiGenResponse:
    """
    This functions decides whether to generate the UI or not based on the user prompt.
    If the user prompt requires UI generation, it generates the UI and returns the response.
    If not, it returns the response without generating the UI.

    :param r_uuid: The UUID for the request; used to create a folder for the outputs
    :param text: The user prompt
    :param console: The rich console object
    :param log_to_console: Whether to log the output to the console
    :return: A `TuiGenResponse` object
    """
    with open("prompts/main.md", "r") as f:
        main_prompt = f.read()

    main_response = model.chat(
        messages=[
            {
                "role": "system",
                "content": main_prompt
            },
            {
                "role": "user",
                "content": text
            }
        ],
        decoding_args=OpenAIDecodingArguments(
            max_tokens=4000,
            temperature=0.5,
            top_p=1.0,
            response_format={"type": "json_object"}
        )
    )
    main_response = MainResponse(**json.loads(main_response["content"]))
    if not main_response.ui_required:
        return TuiGenResponse(
            uuid=r_uuid,
            main_response=main_response,
            html_response="",
            css_response="",
            js_response=""
        )
    if log_to_console:
        console.log("Main response generated.")

    formatted_html_prompt = f"""User Story: {text}
    Plan: {main_response.model_dump_json(indent=4)}"""

    with open("prompts/html_prompt.md", "r") as f:
        html_prompt = f.read()

    html_response = model.chat(
        messages=[
            {
                "role": "system",
                "content": html_prompt
            },
            {
                "role": "user",
                "content": formatted_html_prompt
            }
        ],
        decoding_args=OpenAIDecodingArguments(
            max_tokens=4000,
            temperature=0.5,
            top_p=1.0,
            response_format={"type": "text"}
        )
    )
    try:
        html_response = HTMLResponse(raw_markdown=html_response["content"]).get_html
        if log_to_console:
            console.log("HTML response generated.")
    except Exception as e:
        if log_to_console:
            console.log(f"[bold red]ERROR[/bold red] :: [yellow]app/ui_gen.py[yellow] :: {e}")
        html_response = ""

    formatted_prompt_with_html = f"""User Story: {text}
    Plan: {main_response.model_dump_json(indent=4)}
    HTML: {html_response}"""

    with open("prompts/css_prompt.md", "r") as f:
        css_prompt = f.read()
    with open("prompts/js_prompt.md", "r") as f:
        js_prompt = f.read()

    css_response = model.chat(
        messages=[
            {
                "role": "system",
                "content": css_prompt
            },
            {
                "role": "user",
                "content": formatted_prompt_with_html
            }
        ],
        decoding_args=OpenAIDecodingArguments(
            max_tokens=4000,
            temperature=0.5,
            top_p=1.0,
            response_format={"type": "text"}
        )
    )
    try:
        css_response = CSSResponse(raw_css=css_response["content"]).get_css
        if log_to_console:
            console.log("CSS response generated.")
    except Exception as e:
        if log_to_console:
            console.log(f"[bold red]ERROR[/bold red] :: [yellow]app/ui_gen.py[yellow] :: {e}")
        css_response = ""


    js_response = model.chat(
        messages=[
            {
                "role": "system",
                "content": js_prompt
            },
            {
                "role": "user",
                "content": formatted_prompt_with_html
            }
        ],
        decoding_args=OpenAIDecodingArguments(
            max_tokens=4000,
            temperature=0.5,
            top_p=1.0,
            response_format={"type": "text"}
        )
    )
    try:
        js_response = JSResponse(raw_js=js_response["content"]).get_js
        if log_to_console:
            console.log("JS response generated.")
    except Exception as e:
        if log_to_console:
            console.log(f"[bold red]ERROR[/bold red] :: [yellow]app/ui_gen.py[yellow] :: {e}")
        js_response = ""

    os.makedirs(f"./outputs/{r_uuid}", exist_ok=True)
    with open(f"./outputs/{r_uuid}/main_response.json", "w") as f:
        f.write(main_response.model_dump_json(indent=4))
    with open(f"./outputs/{r_uuid}/index.html", "w") as f:
        f.write(html_response)
    with open(f"./outputs/{r_uuid}/styles.css", "w") as f:
        f.write(css_response)
    with open(f"./outputs/{r_uuid}/script.js", "w") as f:
        f.write(js_response)
    return TuiGenResponse(
        uuid=r_uuid,
        main_response=main_response,
        html_response=html_response,
        css_response=css_response,
        js_response=js_response
    )

