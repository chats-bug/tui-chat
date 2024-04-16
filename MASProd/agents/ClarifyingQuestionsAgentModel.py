import openai
import os
import json
from datetime import datetime
from rich import print, print_json
import asyncio


class ClarifyingQuestionsAgent:
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
        self.questions = []
        
    def get_system_prompt(self):

        #get base prompt

        with open('MASProd/prompts/ClarifyingQuestionsAgent.txt', 'r') as file:
            self.system_prompt = file.read()
            #self.system_prompt = self.system_prompt.replace('{role}', self.role
    
        return self.system_prompt.strip()
    
    
    def chat_completion(self,messages: list):
        
        completion = self.client.chat.completions.create(
        #model="gpt-3.5-turbo-1106",
        model = "gpt-4-1106-preview",
        max_tokens=300,
        temperature=0.2,
        response_format={ "type": "json_object" },
        messages=messages)

        out = dict(completion)
        out = dict(out['choices'][0])
        out = dict(out['message'])
        out = out['content']

        #result = json.loads(out)
        return out
        
        
    def generate_messages(self,prompt) -> list:
    
        formated_messages = [
            {
                'role': 'system',
                'content': f'{prompt}'
            }
        ]
        
         

        return formated_messages
    
    async def generate_response(self,query) :
        with open('MASProd/json/clarifying_questions.json', 'r') as file:
            self.clarifying_questions = json.load(file)

        prompt = self.system_prompt.replace('{given_task}',query)
        prompt = prompt.replace('{task_lists}',str(self.clarifying_questions[self.role]))


        messages = self.generate_messages(prompt)
        # print("-----------------------------------")
        # print("CQA INPUT MESSAGES : ")
        # print(messages)
        # print("-----------------------------------")
        
        
        loop = asyncio.get_event_loop()
        
        bot_message = await loop.run_in_executor(None, lambda:self.chat_completion(messages))
        out = json.loads(bot_message)
        questions = ''
        for i in range(len(self.clarifying_questions[self.role])):
            if self.clarifying_questions[self.role][i]["skill_id"] == out["skill_id"]:
                questions = self.clarifying_questions[self.role][i]["questions"]
                break

        print(bot_message)            
        return str(questions)
    
    
        

    