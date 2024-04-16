import openai
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from agents.ConversationAgentModel import ConversationalAgent
from agents.TaskMinerAgentModel import TaskMiner
from agents.ClarifyingQuestionsAgentModel import ClarifyingQuestionsAgent
from agents.IntegrationAgentModel import IntegrationAgent
from rich import print, print_json
import asyncio
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import time
import hashlib


console = Console()


with open('record.json', 'r') as file:
            review_json_tm = json.load(file)
            print(review_json_tm)
prev_hash = hashlib.md5(str(review_json_tm).encode()).hexdigest()
current_hash = None

while (True):
    with open('record.json', 'r') as file:
            review_json_tm = json.load(file)
            current_hash = hashlib.md5(str(review_json_tm).encode()).hexdigest()  

    json_str_tm = json.dumps(review_json_tm, indent=4)
    syntax_tm = Syntax(json_str_tm, "json", theme="monokai", line_numbers=False,indent_guides=True,word_wrap=True)
    panel_tm = Panel(syntax_tm, title="TASK MINER VIEW", subtitle="Processing done by task miner agent",width=console.width,highlight=True)
    if (prev_hash != current_hash):
        console.print(panel_tm)
        print("")
    else:
           pass