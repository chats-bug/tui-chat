import openai
import os
import json
from datetime import datetime
from rich import print, print_json
import asyncio


class ComplainceAgent:
    def __init__(self,api_key,role):
        self.api_key = api_key
        self.role = role
        self.client = openai.Client(api_key = self.api_key)
        self.system_prompt = self.get_system_prompt()
        self.history = []
        
    def get_system_prompt(self):

        #get base prompt

        with open('MASProd/prompts/ComplianceAgent.txt', 'r') as file:
            self.system_prompt = file.read()
            #self.system_prompt = self.system_prompt.replace('{role}', self.role
    
        return self.system_prompt.strip()
    
    
    def chat_completion(self,messages: list):
        
        completion = self.client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        # model = "gpt-4-1106-preview",
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
        
        
    def generate_messages(self,messages,user_query,t) -> list:
    
        formated_messages = [
            {
                'role': 'system',
                'content': f'{self.system_prompt}'
            }
        ]
        for m in messages:
            
            formated_messages.append({
                'role': 'user',
                'content': m[0]
                          
            })
            formated_messages.append({
                'role': 'assistant',
                #'content': str(json.loads(m[1]))
                'content':m[1]
            })
        
        #print(messages[-1])
        
        formated_messages.append(
            {
                'role': 'user',
                'content': user_query
            }
        )

        #print("-----------------------------------")
        #print(formated_messages)
        #print("-----------------------------------")
         
        self.logging(formated_messages,f'MASProd/logs/{t}/compliance_agent_messages.json')
        return formated_messages
    
    async def generate_response(self,user_query,messages,t) :
        

        prompt = self.system_prompt
        #prompt = prompt.replace('{task_lists}',str(self.clarifying_questions[self.role]))


        messages = self.generate_messages(messages,user_query,t)
        # print("-----------------------------------")
        # print("CQA INPUT MESSAGES : ")
        # print(messages)
        # print("-----------------------------------")
        
        
        loop = asyncio.get_event_loop()
        
        bot_message = await loop.run_in_executor(None, lambda:self.chat_completion(messages))
        out = json.loads(bot_message)
        self.history.append(["Input_for_ComplianceAgent : " + user_query, "ComplianceAgent_Reply_To_ConversationAgent : " + out['instructions_for_ConversationAgent']])
        return str(out['instructions_for_ConversationAgent'])
    
    
    def logging(self,message,file_name):
        with open(file_name, 'w') as file:
            json.dump(message, file, indent=4)  

    