import openai
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from MASProd.agents.ConversationAgentModel import ConversationalAgent
from MASProd.agents.TaskMinerAgentModel import TaskMiner
from MASProd.agents.ClarifyingQuestionsAgentModel import ClarifyingQuestionsAgent
from MASProd.agents.IntegrationAgentModel import IntegrationAgent
from MASProd.agents.ComplainceAgentModel import ComplainceAgent
import asyncio
from rich.console import Console


console = Console()

load_dotenv()

role = "SDR"
api_key = os.getenv("OPEN_AI_API")

conversationalAgent = ConversationalAgent(api_key,role)
minerAgent = TaskMiner(api_key=api_key,role=role)
clarifyingQuestionsAgent = ClarifyingQuestionsAgent(api_key,role)
integrationsAgent = IntegrationAgent(api_key,role)
complainceAgent = ComplainceAgent(api_key,role=role)
Task_list = []


def push_to_task_memory(task_list:list,file_path:str):
    with open(file_path, 'w') as file:
        json.dump(task_list, file, indent=4)


def logging(message,file_name):
    with open(file_name, 'w') as file:
        json.dump(message, file, indent=4)


def timestamp():
    formatted_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    return formatted_time


t = timestamp()
os.mkdir(f"MASProd/logs/{t}")


async def chat_serve(user_prompt: str) -> str:
    async_tasks = [
        asyncio.create_task(minerAgent.generate_response(
            user_prompt, minerAgent.task_list,
            conversationalAgent.conversation_history,
            t
        )),
        asyncio.create_task(complainceAgent.generate_response(
            user_prompt,
            complainceAgent.history,
            t
        )),
    ]
    async_responses = await asyncio.gather(*async_tasks)

    response_task_miner = async_responses[0]
    response_compliance = async_responses[1]

    miner_to_conversation_agent = json.loads(response_task_miner)['instructions_for_ConversationAgent']
    minerAgent.task_list = json.loads(response_task_miner)['Task_list']

    push_to_task_memory(minerAgent.task_list, 'MASProd/json/task_memory.json')

    conversational_agent_query = str(
        {
            "user": user_prompt,
            "MinerAgent": miner_to_conversation_agent,
            "ComplainceAgent": response_compliance,
        }
    )
    response_conversation_agent = conversationalAgent.generate_response(
        conversational_agent_query,
        conversationalAgent.conversation_history,
        t
    )

    logging(conversationalAgent.conversation_history, f"MASProd/logs/{t}/conversation_agent_history.json")
    logging(minerAgent.conversation_history, f"MASProd/logs/{t}/miner_agent_history.json")

    review_json_tm = {
        "Task_Miner_Thought": json.loads(response_task_miner)['thought'],
        "Task_Miner_Analysis": json.loads(response_task_miner)['thought_on_user_CA_chat'],
        "Task_Miner_thought_Super_Agent": json.loads(response_task_miner)['thought_on_Super_Agent'],
        "Task_Miner_Instruction_for_CA": miner_to_conversation_agent
    }

    logging(review_json_tm, "record.json")

    return response_conversation_agent
