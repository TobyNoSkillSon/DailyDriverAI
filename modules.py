import os
import ast
import time
from groq import Groq
from anthropic import Anthropic
from openai import OpenAI
from together import Together
import json
from dotenv import load_dotenv
from typing import List, Optional, Dict, Union, Any, Generator
from together import Together


OPENAI_STD_SUPPORTED = ["Groq", "OpenAI", "TogetherAI"]



def _stream_gen(stream_response, provider):
    if provider in ["Groq", "OpenAI", "TogetherAI"]:
        for chunk in stream_response:
            if hasattr(chunk.choices[0], 'delta'):
                content = chunk.choices[0].delta.content
            elif hasattr(chunk.choices[0], 'text'):
                content = chunk.choices[0].text
            else:
                content = chunk.choices[0].content
            if content is not None:
                yield content

    elif provider == "Anthropic":
        for event in stream_response.events:
            # Check if the event contains a text delta
            if event['type'] == 'content_block_delta' and 'delta' in event['data']:
                yield event['data']['delta']['text']


def _get_client(provider):
    load_dotenv()
    match provider:
        case "Groq":
            return Groq(api_key=os.getenv('GROQ_API_KEY'))
        case "OpenAI":
            return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        case "TogetherAI":
            return Together(api_key=os.getenv("TOGETHER_API_KEY"))
        case "Anthropic":
            return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        case _:
            raise ValueError("Provider not supported.")

def _create_chat_completion_openai_std(client, model, messages, temperature, max_tokens, stop, stream, provider):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stop=stop,
        stream=stream
    )
    if stream:
        return _stream_gen(response, provider)
    else:
        return response.choices[0].message.content

def _create_chat_completion_anthropic(client, model, messages, temperature, max_tokens, stop, stream, provider):
    system_message = "You are a helpfull asistant"
    chat_messages = messages

    if messages and messages[0]['role'] == 'system':
        system_message = messages[0]['content']
        chat_messages = messages[1:]

    response = client.messages.create(
        model=model,
        messages=chat_messages,
        system=system_message,
        max_tokens=max_tokens,
        temperature=temperature,
        stop_sequences=stop,
        # stream=stream    TODO: stream doesn not work skill issue i cnat furgure out how to make te stream gen yield a text sting  
    )

    if stream:
            return response.content[0].text   #_stream_gen(response, provider)
    else:
        return response.content[0].text


def create_chat_completion(
    provider: str,
    model: str,
    messages: List[Dict[str, str]],
    temperature: Optional[float] = 0.7,
    max_tokens: Optional[int] = 3000,
    stop: Optional[List[str]] = None,
    tools: Optional[List[str]] = None,
    stream: Optional[bool] = False
) -> Union[str, Generator]:
    client = _get_client(provider)
    
    if provider in OPENAI_STD_SUPPORTED:
        return _create_chat_completion_openai_std(client, model, messages, temperature, max_tokens, stop, stream, provider)
    elif provider == "Anthropic":
        return _create_chat_completion_anthropic(client, model, messages, temperature, max_tokens, stop, stream, provider)
    else:
        raise ValueError("Provider not supported.")

def create_text_completion(
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: Optional[float] = 0.7,
    max_tokens: Optional[int] = 3000,
    stop: Optional[List[str]] = None,
    tools: Optional[List[str]] = None,
    stream: Optional[bool] = False,
    messages: list = None
) -> Union[str, Generator]:
    """
    This function allows you to send a single message to the API.

    Please note the following when using this function:
    - You can include messages to the LLM, but you must input both a user prompt and a system prompt.
    - The messages should NOT include a system message or a user prompt for which you want a completion.
    """


    if messages == None or messages == []:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    else:
        messages.insert(0, {"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

    return create_chat_completion(
        provider, model, messages, temperature, max_tokens, stop, tools, stream
    )

if __name__ == "__main__":
    for chunk in create_text_completion("Groq", "llama3-70b-8192", "you are a dog","how was your day", stream=True):
        print(chunk, end="")







































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


def create_valid_type_completion(
                self,
                provider: str,
                model: str,
                system_prompt: str,
                user_prompt: str,
                type: type,
                temperature: Optional[float] = 0.7,
                max_tokens: Optional[int] = 256,
                stop: Optional[List[str]] = None,
                tools: Optional[List[str]] = None,
                stream: Optional[bool] = False
            ) -> str:
                client = _get_client(provider)
                # Implementation for creating valid type completion with OpenAI
                pass

