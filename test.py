import json
from rich.console import Console
import uuid
import requests

from app.response_types import MainResponse
from app.ui_gen import ui_gen
from app.ui_gen import TuiGenResponse

console = Console()


def local_test():
    r_uuid = uuid.uuid4()

    with open("chat.json", "r") as f:
        chat = json.load(f)
    task = f"""Here is the user story:
    {json.dumps(chat["messages"], indent=4)}
    """

    print(f"Task: {task}")
    try:
        with console.status("Generating UI..."):
            response = ui_gen(r_uuid, task, console, True)
        console.log(f"UI generated successfully! UUID: ./outputs/{r_uuid}")
    except Exception as e:
        console.print_exception(show_locals=True)
        console.log(f"Failed to generate UI. Error: {e}")


def test_server():
    while True:
        user_input = console.input("\n[bold yellow]User: [/bold yellow]")
        if user_input == "exit":
            break

        url = "http://localhost:8000/tui/chat"
        data = {"text": user_input}

        with console.status("[bold green]Thinking...[/bold green]"):
            response = requests.post(url, json=data)
            response = response.json()

        mas_response = json.loads(response["chat_response"])
        tui_gen_response = TuiGenResponse(**response["tui_gen_response"])
        tui_gen_response.main_response = MainResponse(**response["tui_gen_response"]["main_response"])

        console.print(f"\n[bold green]Assistant:[/bold green] {mas_response['reply_to_user']}")
        if tui_gen_response.main_response.ui_required:
            console.print(f"[bold red]UI:[/bold red] {tui_gen_response.main_response.thoughts}   (./outputs/{tui_gen_response.uuid})")


if __name__ == "__main__":
    test_server()