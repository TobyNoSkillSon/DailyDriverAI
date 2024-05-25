import os
from groq import Groq
from context import Context
import tools
from dotenv import load_dotenv
import json


class Groq_models:
    '''
    This class lets you choose what models
    (avelable at groq) you want to recive response:

    llama3-70b-8192
    llama3-8b-8192
    mixtral-8x7b-32768
    gemma-7b-it
    '''

    MODEL_PARAMS: dict[str, dict[str, int]] = {
        "llama3-8b-8192": {"max_tokens": 8192},
        "llama3-70b-8192": {"max_tokens": 8192},
        "gemma-7b-it": {"max_tokens": 8192},
        "mixtral-8x7b-32768": {"max_tokens": 32768},
    }
        
    def __init__(self) -> None:
        load_dotenv()
        self.key = os.getenv('GROQ_API_KEY')
        self.client = Groq(api_key=self.key)

    def check_model(self, model: str):
        if model not in self.MODEL_PARAMS:
            raise ValueError(f"Model {model} is not supported.")
        return self.MODEL_PARAMS[model]["max_tokens"]

    def handle_stream(self, model: str, max_tokens: int, context: Context):
        text = ''
        stream = self.client.chat.completions.create(
            messages=context.to_list(),
            model=model,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                text += content
                print(content, end="")
        context.add_assistant_message(text)
        return context

    def handle_tool_calls(self, tool_calls, context: Context):
        # available_functions = tools.available_functions()
        # for tool_call in tool_calls:
            # TODO: implement general tool calling

        return None

    def handle_response(self, model: str, max_tokens: int, context: Context):
        response = self.client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=context.to_list(),
            # tools=tools.available_tools(),
            tool_choice="auto",
        )
        response_message = response.choices[0].message.content
        # tool_calls = response_message.tool_calls
        print(response_message)
        context.add_assistant_message(response_message)

        # if tool_calls:
           #  context.add_assistant_message(response.choices[0].message.content)

            # TODO: impLement handle_tools 
            #                              
            # context = self.handle_tool_calls(tool_calls, context)
            # second_response = self.client.chat.completions.create(
            #     model=model,
            #     messages=context.to_list()
            # )
            # print(second_response.choices[0].message.content)
            # context.add_assistant_message(second_response.choices[0].message.content)
        # else:
            # context.add_assistant_message(response.choices[0].message.content)
        return context

    def send_request(self, model: str, context: Context = None, tools: bool=False) -> (Context | str):
        '''
        Sends a request to the specified model and adds the response to the context.
        '''
        max_tokens = self.check_model(model)
        if tools:
            context = self.handle_response(model, max_tokens, context)
        else:
            context = self.handle_stream(model, max_tokens, context)
        return context


