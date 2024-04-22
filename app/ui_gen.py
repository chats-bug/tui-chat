import json
import os
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from dotenv import load_dotenv
from pydantic import BaseModel
from rich.console import Console

from app.response_types import MainResponse, HTMLResponse, CSSResponse, JSResponse
from llm import OpenAIDecodingArguments, OpenAiModel, OpenAiChatModels
from concurrent.futures import ThreadPoolExecutor


load_dotenv()
console = Console()


# Initialize the OpenAI model
model = OpenAiModel(
    model=OpenAiChatModels.GPT_4_TURBO_PREVIEW,
    api_key=os.getenv("OPENAI_API_KEY"),
)


class TuiGenResponse(BaseModel):
    uuid: UUID
    main_response: MainResponse
    html_response: str
    css_response: Optional[str]
    js_response: Optional[str]

    class Config:
        from_attributes = True


def ui_gen(
    r_uuid: UUID,
    text: str,
    console: Console = console,
    log_to_console: bool = False,
    multiprocessing: bool = False,
) -> TuiGenResponse:
    """
    This functions decides whether to generate the UI or not based on the user prompt.
    If the user prompt requires UI generation, it generates the UI and returns the response.
    If not, it returns the response without generating the UI.

    :param r_uuid: The UUID for the request; used to create a folder for the outputs
    :param text: The user prompt
    :param console: The rich console object
    :param log_to_console: Whether to log the output to the console
    :param multiprocessing: Whether to use multiprocessing to generate the code
    :return: A `TuiGenResponse` object
    """
    with open("prompts/main.md", "r") as f:
        main_prompt = f.read()

    if log_to_console:
        with console.status("[bold green]Deciding on UI...[/bold green]"):
            main_response = model.chat(
                messages=[
                    {"role": "system", "content": main_prompt},
                    {"role": "user", "content": text},
                ],
                decoding_args=OpenAIDecodingArguments(
                    max_tokens=4000,
                    temperature=0,
                    top_p=1,
                    response_format={"type": "json_object"},
                ),
            )
    else:
        main_response = model.chat(
            messages=[
                {"role": "system", "content": main_prompt},
                {"role": "user", "content": text},
            ],
            decoding_args=OpenAIDecodingArguments(
                max_tokens=4000,
                temperature=0,
                top_p=1.0,
                response_format={"type": "json_object"},
            ),
        )

    main_response = MainResponse(**json.loads(main_response["content"]))
    if log_to_console:
        console.log("[bold yellow]Main response[/bold yellow]: ", main_response, "\n")
    if not main_response.ui_required:
        return TuiGenResponse(
            uuid=r_uuid,
            main_response=main_response,
            html_response="",
            css_response="",
            js_response="",
        )

    # formatted_html_prompt = f"""User Story: {text}
    # Plan: {main_response.model_dump_json(indent=4)}"""
    formatted_html_prompt = f"""User Story: {text}"""

    # html_response, css_response, js_response = generate_all_code(
    #     prompt=formatted_html_prompt,
    #     r_uuid=r_uuid,
    #     console=console,
    #     multi_processing=multiprocessing,
    # )
    if log_to_console:
        with console.status("[bold green]Generating UI...[/bold green]"):
            html_response, css_response, js_response = generate_all_code_tailwind(
                prompt=formatted_html_prompt,
                r_uuid=r_uuid,
                console=console,
                multi_processing=multiprocessing,
            )
    else:
        html_response, css_response, js_response = generate_all_code_tailwind(
            prompt=formatted_html_prompt,
            r_uuid=r_uuid,
            console=console,
            multi_processing=multiprocessing,
        )

    return TuiGenResponse(
        uuid=r_uuid,
        main_response=main_response,
        html_response=html_response,
        css_response=css_response,
        js_response=js_response,
    )


def generate_all_code(
    prompt: str,
    r_uuid: UUID,
    console: Console = console,
    multi_processing: bool = False,
):
    html_prompt_file_path = "prompts/html_prompt.md"
    css_prompt_file_path = "prompts/css_prompt.md"
    js_prompt_file_path = "prompts/js_prompt.md"

    if multi_processing:
        num_workers = 3
        console.log("Spawning 3 workers to generate HTML, CSS, and JS code.")
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            results = executor.map(
                generate_code,
                [prompt] * num_workers,
                [html_prompt_file_path, css_prompt_file_path, js_prompt_file_path],
                [HTMLResponse, CSSResponse, JSResponse],
            )
    else:
        results = [
            generate_code(prompt, html_prompt_file_path, HTMLResponse),
            generate_code(prompt, css_prompt_file_path, CSSResponse),
            generate_code(prompt, js_prompt_file_path, JSResponse),
        ]

    html_response, css_response, js_response = results
    console.log("Code generation complete.")

    os.makedirs(f"./outputs/{r_uuid}", exist_ok=True)
    try:
        html_response = html_response.get_html
    except:
        html_response = html_response.raw
        console.log(
            f"[bold red]ERROR[/bold red] :: [yellow]app/ui_gen.py[yellow] :: HTML response not properly generated"
        )
    try:
        css_response = css_response.get_css
    except:
        css_response = css_response.raw
        console.log(
            f"[bold red]ERROR[/bold red] :: [yellow]app/ui_gen.py[yellow] :: CSS response not properly generated"
        )
    try:
        js_response = js_response.get_js
    except:
        js_response = js_response.raw
        console.log(
            f"[bold red]ERROR[/bold red] :: [yellow]app/ui_gen.py[yellow] :: JS response not properly generated"
        )

    with open(f"./outputs/{r_uuid}/index.html", "w") as f:
        f.write(html_response)

    with open(f"./outputs/{r_uuid}/styles.css", "w") as f:
        f.write(css_response)

    with open(f"./outputs/{r_uuid}/script.js", "w") as f:
        f.write(js_response)

    return html_response, css_response, js_response


def generate_all_code_tailwind(
    prompt: str,
    r_uuid: UUID,
    console: Console = console,
    multi_processing: bool = False,
):
    html_prompt_file_path = "prompts/custom_html_prompt.md"
    js_prompt_file_path = "prompts/js_prompt.md"

    # html_response = generate_code(prompt, html_prompt_file_path, HTMLResponse)
    # js_response = generate_code(prompt, js_prompt_file_path, JSResponse)

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = executor.map(
            generate_code,
            [prompt] * 2,
            [html_prompt_file_path, js_prompt_file_path],
            [HTMLResponse, JSResponse],
        )

    html_response, js_response = results
    try:
        html_response = html_response.get_html
    except:
        html_response = html_response.raw
        console.log(
            f"[bold red]ERROR[/bold red] :: [yellow]app/ui_gen.py[yellow] :: HTML response not properly generated"
        )

    # formatted_js_prompt = f"""User Story: {prompt}
    # HTML: {html_response}"""

    try:
        js_response = js_response.get_js
    except:
        js_response = js_response.raw
        console.log(
            f"[bold red]ERROR[/bold red] :: [yellow]app/ui_gen.py[yellow] :: JS response not properly generated"
        )

    console.log("Code generation complete.")

    os.makedirs(f"./outputs/{r_uuid}", exist_ok=True)

    with open(f"./outputs/{r_uuid}/index.html", "w") as f:
        f.write(html_response)
    with open(f"./outputs/{r_uuid}/script.js", "w") as f:
        f.write(js_response)

    # with open(f"./outputs/{r_uuid}/script.js", "w") as f:
    #     f.write(js_response)

    return html_response, "", js_response


def generate_code(
    prompt: str,
    system_prompt_file_path: str,
    parse_class=None,
):
    with open(system_prompt_file_path, "r") as f:
        system_prompt = f.read()

    response = model.chat(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        decoding_args=OpenAIDecodingArguments(
            max_tokens=4000,
            temperature=0,
            top_p=1.0,
            response_format={"type": "text"},
        ),
    )
    if parse_class is not None:
        try:
            response = parse_class(raw_markdown=response["content"])
        except Exception as e:
            response = None
    else:
        response = response["content"]

    return response
