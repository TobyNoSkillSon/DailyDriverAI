
from dotenv import load_dotenv
from groq import Groq
import time
import ast
import os


def send_request(model: str, system_prompt: str, user_prompt: str) -> str:
        '''
        Sends a simple request to the specified model
        '''
        load_dotenv()
        key = os.getenv('GROQ_API_KEY')
        client = Groq(api_key=key)

        max_tokens = 8192
        template = [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{user_prompt}"}
            ]
        
        response = client.chat.completions.create(
                model=model,
                messages= template,
                max_tokens=max_tokens
            )
        return response.choices[0].message.content



class Custom_agent:
    def __init__(self, agent_system_promt: str) -> None:
        self.system_prompt = agent_system_promt
        
    def send_request_return_type(self, user_prompt: str, return_type: type) -> type:
        '''This function ensures that the response is converted correctly to the desired type list, int, dict ect.
        There are 10 retries, if all of them fail, retuns None'''
        max_retries = 10
        attempts = 0
        while attempts < max_retries:
            try:
                print("Trying to send request")
                response = ast.literal_eval(send_request("llama3-70b-8192", self.system_prompt, user_prompt))
                if isinstance(response, return_type):
                    return response
            except Exception as e:
                attempts += 1
                print(f"Attempt {attempts}/{max_retries} failed due to: {e}. Retrying in 2 seconds...")
                time.sleep(2)
        print(f"agent failed after maximum attempts")

