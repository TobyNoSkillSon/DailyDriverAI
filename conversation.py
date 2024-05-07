import os
from groq import Groq
from context import Context
import tools
from dotenv import load_dotenv




def run_conversation(user_prompt:str, system_prompt:str, model_name:str, context: Context):
    
    MODEL_PARAMS: dict[str, dict[str, int]] = {
        "llama3-8b-8192": {"max_tokens": 8192},
        "llama3-70b-8192": {"max_tokens": 8192},
        "gemma-7b-it": {"max_tokens": 8192},
        "mixtral-8x7b-32768": {"max_tokens": 32768},
    }
    if model_name not in MODEL_PARAMS:
            raise ValueError(f"Model {model_name} is not supported.")
    max_tokens = MODEL_PARAMS[model_name]["max_tokens"]

    
    load_dotenv()
    key = os.getenv('GROQ_API_KEY')
    client = Groq(api_key=key)

    response = client.chat.completions.create(
        model=model_name,
        max_tokens=max_tokens,
        messages=context,
        tools=tools.avelable_tools(),
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    if tool_calls:
        available_functions = tools.avelable_functions()
        context.add_assistant_message(response_message) 

        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]

            function_args = json.loads(tool_call.function.arguments)
            
            function_response = function_to_call(
                team_name=function_args.get("team_name")
            )
            context.add_tool_message(tool_call.id, function_name, function_response) 
            # extend conversation with function response
        
        
        second_response = client.chat.completions.create(
            model=model_name,
            messages=context
        )  
        context.add_assistant_message(second_response.choices[0].message.content)
        return context
    else:
        return context
    



class Groq_models:
    '''
    This class lets you choose what models
    (avelable at groq) you want to recive response:

    llama3-70b-8192
    llama3-8b-8192
    mixtral-8x7b-32768
    gemma-7b-it
    '''

    

    def __init__(self) -> None:
        load_dotenv()
        self.key = os.getenv('GROQ_API_KEY')
        self.client = Groq(api_key=self.key)


    def send_request(self, system_prompt: str, user_prompt: str, model: str, context: Context = None, stream: bool=False) -> (Context | str):
        '''
        Sends a request to the specified model and adds the response to the context.
        '''
        
        context.add_system_message(system_prompt)
        
        
        context.add_user_message(user_prompt)
        
        if stream:
            text = ''
            stream = self.client.chat.completions.create(
                messages=context.to_list(),
                model=model,
                ,
                stream=True,
            )
            
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content is not None:
                    text += content
                    print(content, end="")
            context.add_assistant_message(text)
        else:
            response = self.client.chat.completions.create(
                model=model,
                messages=context.to_list(), 
                max_tokens=max_tokens
            )
            context.add_assistant_message(response.choices[0].message.content)
        
        context.delete_system_message()
        return context

