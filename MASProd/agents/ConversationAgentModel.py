import openai
import json

from dotenv import load_dotenv

load_dotenv()


class ConversationalAgent:
    def __init__(self,api_key,role):
        self.api_key = api_key
        self.role = role
        self.conversation_history = []
        self.client = openai.Client(api_key = self.api_key)
        self.thoughts = []
        self.system_prompt = self.get_system_prompt()    
        
    def get_system_prompt(self):

        #get base prompt

        with open('MASProd/prompts/ConversationAgent.txt', 'r') as file:
            self.system_prompt = file.read()
            self.system_prompt = self.system_prompt.replace('{role}', self.role)

        #get skills 
            
        with open('MASProd/json/skill.json','r') as file:
            self.skills = json.load(file)
            self.system_prompt = self.system_prompt.replace('{skills}', str(self.skills[self.role]['skills']))
    
        return self.system_prompt.strip()
    

    def chat_completion(self,messages: list):
        try:
            completion = self.client.chat.completions.create(
            model = "gpt-4-turbo-preview",
            max_tokens=600,
            temperature=0.2,
            response_format={ "type": "json_object" },
            messages=messages)

            out = dict(completion)
            out = dict(out['choices'][0])
            out = dict(out['message'])
            out = out['content']
            return out
        except:
            return 'We are facing a technical issue at this moment.'
        
    def generate_messages(self,messages: list, query: str,t) -> list:
    
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
                'content': query
            }
        )

        #print("-----------------------------------")
        #print(formated_messages)
        #print("-----------------------------------")
            
        self.logging(formated_messages,f'MASProd/logs/{t}/conversation_agent_messages.json')
        return formated_messages
    
    def generate_response(self,query: str, chat_history: list,t) :
        
        # if len(chat_history) > 5 :
        #     chat_history = chat_history[-5:]
        
        messages = self.generate_messages(chat_history, query,t)
        
        # print("-----------------------------------")
        # print("CONVERSATION AGENT INPUT MESSAGES : ")
        # print(messages)
        # print("-----------------------------------")
        bot_message = self.chat_completion(messages)
        #miner.conversation_history.append([query,miner_response])
        # miner_response = miner.generate_response(chat_history = chat_history,query=query)
        # print("#"*30) 
        # print(miner_response)
        # print("#"*30)
        reply_to_user = json.loads(bot_message)['reply_to_user']
        #self.conversation_history.append([query, bot_message])
        self.conversation_history.append(["Input for ConversationAgent : " + query, "ConversationAgent_Reply_To_User : " + reply_to_user])
        
        #self.conversation_history = chat_history
        #print("Number of message packs being send for CA: ",len(chat_history))
        
        #print(self.conversation_history)
        return bot_message
    
    def logging(self,message,file_name):
        with open(file_name, 'w') as file:
            json.dump(message, file, indent=4)