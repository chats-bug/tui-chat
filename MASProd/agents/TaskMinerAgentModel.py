import openai
import os
import json
from datetime import datetime
from rich import print, print_json
import asyncio


class TaskMiner:
    def __init__(self,api_key,role):
        self.api_key = api_key
        self.role = role
        self.conversation_history = []
        self.client = openai.Client(api_key = self.api_key)
        self.thoughts = []
        self.system_prompt = self.get_system_prompt()
        self.task_list = []
        self.clarifying_questions = None
        self.expert_prompt = None
        self.new_system_prompt = self.system_prompt
        self.previous_current_task_id = None
        self.last_message = '[]'
        
    def get_system_prompt(self):

        #get base prompt

        with open('MASProd/prompts/TaskMinerAgent.txt', 'r') as file:
            self.system_prompt = file.read()
            #self.system_prompt = self.system_prompt.replace('{role}', self.role)

        #get skills 
            
        with open('MASProd/json/skill.json','r') as file:
            self.skills = json.load(file)
            self.system_prompt = self.system_prompt.replace('{skills}', str(self.skills[self.role]['skills']))
    
        return self.system_prompt.strip()
    
    
    def chat_completion(self,messages: list):
        
        completion = self.client.chat.completions.create(
        model="gpt-4-1106-preview",
        #model = "gpt-4-0125-preview",
        max_tokens=1500,
        temperature=0.2,
        response_format={ "type": "json_object" },
        messages=messages)

        out = dict(completion)
        out = dict(out['choices'][0])
        out = dict(out['message'])
        out = out['content']

        #result = json.loads(out)
        return out
        
        
    def generate_messages(self,task_list,conversation_history, query,t) -> list:
    
        formated_messages = [
            {
                'role': 'system',
                'content': f'{self.system_prompt}'
            }
        ]
        
        formated_messages.append({
                'role':'user',
                'content':"Recent Chat history between user and ConversationAgent : \n" + str(conversation_history)
            })
        try:
            ifca = "instructions_for_ConversationAgent : " + json.loads(self.last_message)['instructions_for_ConversationAgent']
            ctid = "current_task_id : " + json.loads(self.last_message)['current_task_id']
        except:
            ifca = ''
            ctid = ''
        formated_messages.append(
            {
                'role': 'assistant',
                'content':  "\nPending task_id to be mined : " + self.find_pending_task_ids('MASProd/json/task_memory.json') + "\n" + ifca + "\nTask_list : " + str(self.update_assistant_memory('MASProd/json/task_memory.json')) + "\n" + ctid
                
            }
        )    
        
        formated_messages.append(
            {
                'role': 'user',
                'content': query
            }
        )

        #print("-----------------------------------")
        #print(formated_messages)
        #print("-----------------------------------")
        self.logging(formated_messages,f'MASProd/logs/{t}/task_miner_messages.json')

        return formated_messages
    
    async def generate_response(self,query,task_list,conversation_history,t) :
        
        messages = self.generate_messages(task_list,conversation_history, query,t)
        loop = asyncio.get_event_loop()
        bot_message = await loop.run_in_executor(None, lambda:self.chat_completion(messages))
        self.conversation_history.append([query,bot_message])
        self.last_message = str(bot_message)
        return bot_message
    
    def update_assistant_memory(self,file_path:str):
        try:
            with open(file_path, 'r') as file:
                task_memory = json.load(file)
                return task_memory
        except:

            return "[]"
    
    def logging(self,message,file_name):
        with open(file_name, 'w') as file:
            json.dump(message, file, indent=4)

    def find_pending_task_ids(self, file_path):
        try:
            pending_task_ids = []
            # Iterate through each task in the Task_list
            with open(file_path, 'r') as file:
                task_memory = json.load(file)
                for task in (task_memory):
                # Check if the mining_status is 'pending'
                    if task.get("mining_status") == "pending":
                    # Append the task_id to the list
                        pending_task_ids.append(task.get("task_id"))
                #print(pending_task_ids)
                return (str(pending_task_ids))
            
            
        except:
            return ''