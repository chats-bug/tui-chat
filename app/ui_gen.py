import json
import os
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


def ui_gen(r_uuid, text, log_to_console: bool = False):
    """

    :param r_uuid: The UUID for the request; used to create a folder for the outputs
    :param text: The user prompt
    :param log_to_console: Whether to log the output to the console
    :return:
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
    html_response = HTMLResponse(raw_markdown=html_response["content"])
    if log_to_console:
        console.log("HTML response generated.")

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
    css_response = CSSResponse(raw_css=css_response["content"])
    if log_to_console:
        console.log("CSS response generated.")


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
    js_response = JSResponse(raw_js=js_response["content"])
    if log_to_console:
        console.log("JS response generated.")

    os.makedirs(f"./outputs/{r_uuid}", exist_ok=True)
    with open(f"./outputs/{r_uuid}/main_response.json", "w") as f:
        f.write(main_response.model_dump_json(indent=4))
    with open(f"./outputs/{r_uuid}/html_response.html", "w") as f:
        f.write(html_response.get_html)
    with open(f"./outputs/{r_uuid}/css_response.css", "w") as f:
        f.write(css_response.get_css)
    with open(f"./outputs/{r_uuid}/js_response.js", "w") as f:
        f.write(js_response.get_js)
    return {
        "uuid": str(r_uuid),
        "main_response": main_response,
        "html_response": html_response.get_html,
        "css_response": css_response.get_css,
        "js_response": js_response.get_js,
    }

