from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from rich.console import Console

load_dotenv()
console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_gpt(
        prompt: Optional[str] = None,
        temperature: float = 0.3,
        top_p: float = 0.5,
        frequency_penalty: int = 1,
        presence_penalty: int = 1,
        max_tokens: int = 1500,
        system_message_path: Optional[str] = None,
        response_format: Optional[dict] = None
):
    if response_format is None:
        response_format = {"type": "text"}

    if system_message_path:
        with open(system_message_path, "r") as file:
            system_message = file.read()
    else:
        system_message = "You are a helpful assistant that is here to help the user with their queries."

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        response_format=response_format
    )

    content = response.choices[0].message.content
    return content


def parse_response(response):
    """
    The response would be a markdown of the following format:
    ```markdown
      ## **Requirement**
      {describe here if a renderable is required. If not, skip the rest of the sections}

      ## **HTML**
      {html content here}

      ## **CSS**
      {css content here}

      ## **Javascript**
      {js code here}
    ```

    Parse the response into a dictionary of the following format:
    {
        "requirement": str,
        "html": str,
        "css": str,
        "js": str
    }
    Also make an output directory and save the html, css, and js files there.

    :param response:
    :return: list[dict]
    """
    # Split the response into the different sections
    sections = response.split("##")
    sections = [section.strip() for section in sections]

    # Parse the sections
    parsed_response = {}
    for section in sections:
        if section.startswith("**Requirement**"):
            parsed_response["requirement"] = section.split("**Requirement**")[1].strip()
        elif section.startswith("**HTML**"):
            parsed_response["html"] = section.split("**HTML**")[1].strip()
            # check if it starts with a code block and ends with a code block
            if parsed_response["html"].startswith("```html"):
                parsed_response["html"] = (
                    parsed_response["html"].split("```html")[1].strip()
                )
            if parsed_response["html"].endswith("```"):
                parsed_response["html"] = (
                    parsed_response["html"].split("```")[0].strip()
                )
        elif section.startswith("**CSS**"):
            parsed_response["css"] = section.split("**CSS**")[1].strip()
            if parsed_response["css"].startswith("```css"):
                parsed_response["css"] = (
                    parsed_response["css"].split("```css")[1].strip()
                )
            if parsed_response["css"].endswith("```"):
                parsed_response["css"] = parsed_response["css"].split("```")[0].strip()
        elif section.startswith("**Javascript**"):
            parsed_response["js"] = section.split("**Javascript**")[1].strip()
            if parsed_response["js"].startswith("```javascript"):
                parsed_response["js"] = (
                    parsed_response["js"].split("```javascript")[1].strip()
                )
            if parsed_response["js"].endswith("```"):
                parsed_response["js"] = parsed_response["js"].split("```")[0].strip()

    if not os.path.exists("output"):
        os.makedirs("output")

    # Save the files
    with open("output/index.html", "w") as file:
        file.write(parsed_response["html"])
    console.log("HTML saved in output/index.html")

    with open("output/style.css", "w") as file:
        file.write(parsed_response["css"])
    console.log("CSS saved in output/style.css")

    with open("output/script.js", "w") as file:
        file.write(parsed_response["js"])
    console.log("Javascript saved in output/script.js")

    return parsed_response


def parse_json_response(response):
    """
    :param response:
    :return: dict
    """
    parsed_response = json.loads(response)

    if not os.path.exists("output_2"):
        os.makedirs("output_2")

    # Save the files
    if "html" in parsed_response:
        with open("output_2/index.html", "w") as file:
            file.write(parsed_response["html"])
        console.log("HTML saved in output/index.html")

    if "css" in parsed_response:
        with open("output_2/style.css", "w") as file:
            file.write(parsed_response["css"])
        console.log("CSS saved in output/style.css")

    if "javascript" in parsed_response:
        with open("output_2/script.js", "w") as file:
            file.write(parsed_response["javascript"])
        console.log("Javascript saved in output/script.js")

    return parsed_response


def run():
    # Read the messages
    with open("chat.json", "r") as file:
        messages = json.load(file)

    # Call the GPT model
    console.log("Calling the GPT model...")
    with console.status("[bold green]Generating response..."):
        response = call_gpt(
            prompt=json.dumps(messages),
            system_message_path="prompts/prompt.md",
            response_format={"type": "json_object"},
        )
    console.log("Response generated successfully!")

    # Save the response
    if response.startswith("```json"):
        response = response.split("```json")[1].strip()
    if response.startswith("```"):
        response = response.split("```")[1].strip()
    if response.endswith("```"):
        response = response.split("```")[0].strip()
    with open("response.json", "w") as file:
        json.dump(json.loads(response), file, indent=4)
    console.log("Response saved successfully!")

    # Parse the response
    parsed_response = parse_json_response(response)


if __name__ == "__main__":
    try:
        run()
    except Exception:
        console.print_exception()
