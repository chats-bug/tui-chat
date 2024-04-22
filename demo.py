import json
import time
from rich.console import Console
import uuid
import requests

from app.response_types import MainResponse
from app.ui_gen import ui_gen
from app.ui_gen import TuiGenResponse
import questionary


console = Console()


def simulate_chat():
    messages = ""
    while True:
        user_input = questionary.text("👦 User: ").ask()
        if user_input == "exit":
            break
        assistant_response_simulated = questionary.text("🤖 Assistant: ").ask()
        console.print()

        messages += f"User: {user_input}\nAssistant: {assistant_response_simulated}"
        formatted_text = messages
        # Send this formatted_text to ui_gen
        r_uuid = uuid.uuid4()
        with console.status("[bold green]Thinking 'bout UI...[/bold green]"):
            tui_gen_response = ui_gen(r_uuid, formatted_text, console, True, True)

        if tui_gen_response.main_response.ui_required:
            console.print(
                f"[bold red]UI:[/bold red] {tui_gen_response.main_response.thoughts}   (./outputs/{tui_gen_response.uuid})\n"
            )
            messages += "TUI: UI generated for the request successfully!\n"
        else:
            messages += "TUI: No UI required for the request.\n"


def chat_demo():
    with open("script.json", "r") as f:
        script = json.load(f)
    messages = script["messages"]

    for i in range(1, len(messages), 2):
        user_input = questionary.text("👦 User: ").ask()
        if user_input == "exit":
            break

        with console.status("[bold green]Thinking...[/bold green]"):
            time.sleep(0.3)
            assistant_response = messages[i].split("Bot: ")[1]
            console.print(f"🤖 Assistant: {assistant_response}")

        r_uuid = uuid.uuid4()
        tui_gen_response = ui_gen(
            uuid.uuid4(),
            f"User: {user_input}\nAssistant: {assistant_response}",
            console,
            True,
            True,
        )

        if tui_gen_response.main_response.ui_required:
            console.print(
                f"[bold red]UI:[/bold red] {tui_gen_response.main_response.thoughts}   (./outputs/{tui_gen_response.uuid})\n"
            )


if __name__ == "__main__":
    # chat_demo()
    test_prompt = """User: Do I have any emails?
    Bot: Alright. During the next week these are your free slots:
    {
        "Monday": ["09:00 - 11:00", "13:30 - 15:30", "16:00 - 18:00"],
        "Tuesday": ["10:00 - 12:00", "14:30 - 16:30"],
        "Wednesday": ["08:00 - 10:00", "11:30 - 13:30", "15:00 - 17:00"],
        "Thursday": ["09:30 - 11:30", "13:00 - 15:00", "16:30 - 18:30"],
        "Friday": ["08:30 - 10:30", "12:00 - 14:00", "15:30 - 17:30"]
    }.
    Also could you please provide the following details: Agenda for the meeting, Invitees (including Sarah Johnson), duration any additional notes.
    """
    tui_gen_response = ui_gen(
        uuid.uuid4(),
        test_prompt,
        console,
        True,
        True,
    )
    console.log(f"UI generated successfully! UUID: ./outputs/{tui_gen_response.uuid}")
