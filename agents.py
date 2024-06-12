from typing import Union, Generator, Any
from context import Context
from openai import OpenAI
from dotenv import load_dotenv
from groq import Groq
import os
import time
import ast

class CustomAgent:
    MODEL_PARAMS: dict[str, dict[str, int]] = {
        "llama3-8b-8192": {"max_tokens": 8192, "provider": "Groq"},
        "llama3-70b-8192": {"max_tokens": 8192, "provider": "Groq"},
        "gemma-7b-it": {"max_tokens": 8192, "provider": "Groq"},
        "mixtral-8x7b-32768": {"max_tokens": 32768, "provider": "Groq"},
        "gpt-4o": {"max_tokens": 1000, "provider": "Openai"},
        "gpt-3.5-turbo": {"max_tokens": 1000, "provider": "Openai"}
    }

    def __init__(self, agent_system_prompt: str, model: str, context: Context = None) -> None:
        self.system_prompt = agent_system_prompt
        if context == None:
            self.context = Context()
            self.context.add_system_message(agent_system_prompt)
        else:
            self.context = context

        
        self.model = model
        if self.model not in self.MODEL_PARAMS:
            raise ValueError(f"Model {self.model} is not supported.")
        
        self.max_tokens = self.MODEL_PARAMS[self.model]["max_tokens"]
        self.provider = self.MODEL_PARAMS[self.model]["provider"]

        load_dotenv()
        if self.provider == "Groq":
            self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        elif self.provider == "Openai":
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        else: raise ValueError (f"Provider '{self.provider}' is not supported.")
        



    def change_model(self, new_model:str):
        self.model= new_model
        self.max_tokens = self.MODEL_PARAMS[self.model]["max_tokens"]
        self.provider = self.MODEL_PARAMS[self.model]["provider"]

        if self.provider == "Groq":
            self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        elif self.provider == "Openai":
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        else: raise ValueError (f"Provider '{self.provider}' is not supported.")


    def _groq_stream_gen(self, stream_response):
            text = ''
            for chunk in stream_response:
                content = chunk.choices[0].delta.content
                if content is not None:
                    text+= content
                    yield content
            self.context.add_assistant_message(text)

    def _groq_send_request(self, user_prompt: str, stream: bool = False) -> Union[Generator[str, Any, None], Context]:
        self.context.add_user_message(user_prompt)
        if stream:
            stream_response = self.client.chat.completions.create(
                messages=self.context.to_list(),
                model=self.model,
                max_tokens=self.max_tokens,
                stream=True,
            )
            return self._groq_stream_gen(stream_response)
        else:
            response = self.client.chat.completions.create(
                messages=self.context.to_list(),
                model=self.model,
                max_tokens=self.max_tokens,
            )
            text = response.choices[0].message.content
            self.context.add_assistant_message(text)
            return self.context


    def _openai_stream_gen(self, stream_response):
        text = ''
        for chunk in stream_response:
            content = chunk.choices[0].delta.content
            if content is not None:
                text += content
                yield content
        self.context.add_assistant_message(text)

    def _openai_send_request(self, user_prompt: str, stream: bool = False) -> Union[Generator[str, Any, None], Context]:
        self.context.add_user_message(user_prompt)
        if stream:
            stream_response = self.client.chat.completions.create(
                messages=self.context.to_list(),
                model=self.model,
                max_tokens=self.max_tokens,
                stream=True
            )
            return self._openai_stream_gen(stream_response)
        else:
            response = self.client.chat.completions.create(
                messages=self.context.to_list(),
                model=self.model,
                max_tokens=self.max_tokens
            )
            text = response.choices[0].message.content
            self.context.add_assistant_message(text)
            return self.context

    def send_request(self, user_prompt: str, stream: bool = False) -> Union[Generator[str, Any, None], Context]:
        # TODO: this funciton needs docs string
        if self.provider == "Openai":
            return self._openai_send_request(user_prompt, stream)
        elif self.provider == "Groq":
            return self._groq_send_request(user_prompt, stream)








    def _openai_send_tool_request(self, user_prompt: str, stream: bool = False) -> Union[Generator[str, Any, None], Context]:
        pass



    def _groq_send_tool_request(self, user_prompt: str, stream: bool = False) -> Union[Generator[str, Any, None], Context]:
        pass




    def send_tool_request(self, user_prompt: str, stream: bool = False) -> Union[Generator[str, Any, None], Context]:
        # TODO: this funciton needs docs string
        if self.provider == "Openai":
            return self._openai_send_tool_request(user_prompt, stream)
        elif self.provider == "Groq":
            return self._groq_send_tool_request(user_prompt, stream)

        self.context.add_user_message(user_prompt)
        if stream:
            stream_response = self.client.chat.completions.create(
                messages=self.context.to_list(),
                model=self.model,
                max_tokens=self.max_tokens,
                tool_choice="auto",
                stream=True,
            )
            if self.provider == "Groq":
                return self._groq_stream_gen(stream_response)
            elif self.provider == "Openai":
                return self._openai_stream_gen(stream_response)
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=self.context.to_list(),
                tool_choice="auto",
            )
            if self.provider == "Groq":
                text = response.choices[0].message.content
                self.context.add_assistant_message(text)
                return self.context
            elif self.provider == "Openai":
                text = response.choices[0].message['content']
                self.context.add_assistant_message(text)
                return self.context






    # TODO: time to implement provider specific send_tools_request and rename the base function to send_tool_request
    def send_tools_request(self, user_prompt: str, stream: bool = False) -> Union[Generator[str, Any, None], Context]:
        '''
        Sends a tools-enabled request to the specified model and adds the response to the context.
        If streaming is enabled, yields content from each chunk.
        '''
        self.context.add_user_message(user_prompt)

        if stream:
            stream_response = self.client.chat.completions.create(
                messages=self.context.to_list(),
                model=self.model,
                max_tokens=self.max_tokens,
                tool_choice="auto",
                stream=True,
            )
            return self._stream_gen(stream_response)
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=self.context.to_list(),
                tool_choice="auto",
            )
            response_message = response.choices[0].message.content
            self.context.add_assistant_message(response_message)
            return self.context


    def send_request_return_type(self, user_prompt: str, return_type: type, tools: bool = False) -> type:
        '''This function ensures that the response is converted correctly to the desired type list, int, dict, etc.
        There are 10 retries, if all of them fail, returns None'''
        max_retries = 10
        attempts = 0
        while attempts < max_retries:
            try:
                print("Trying to send request")
                last_message = self.send_request(user_prompt).get_last_message()["content"]
                self.context.delete_last_message(2)
                response = ast.literal_eval(last_message)
                if isinstance(response, return_type):
                    return response
            except Exception as e:
                attempts += 1
                print(f"Attempt {attempts}/{max_retries} failed due to: {e}. Retrying in 2 seconds...")
                time.sleep(2)
        print(f"Agent failed after maximum attempts")
        return None
    
    


if __name__ == "__main__":
    test = CustomAgent("YOU are an algorithm that outputs a python valid list of ints. nothing else", "llama3-8b-8192")
    print(test.send_request_return_type("how are you", list))