from typing import Union, Callable, Generator, Any
from context import Context
import modules



class CustomAgent:
    MODEL_PARAMS: dict[str, dict[str, int]] = {
        "llama3-8b-8192": {"max_tokens": 8192},
        "llama3-70b-8192": {"max_tokens": 8192},
        "gemma-7b-it": {"max_tokens": 8192},
        "mixtral-8x7b-32768": {"max_tokens": 32768},
        "gpt-4o": {"max_tokens": 128000},
        "gpt-3.5-turbo": {"max_tokens": 16385},
        "mistralai/Mixtral-8x7B-Instruct-v0.1":{"max_tokens": 32768},
        "claude-3-opus-20240229":{"max_tokens": 20240307}, 
        "claude-3-5-sonnet-20240620":{"max_tokens": 20240307}, 
        "claude-3-haiku-20240307":{"max_tokens": 20240307},
        "Qwen/Qwen2-72B-Instruct":{"max_tokens": 131072},
        "gemma2-9b-it": {"max_tokens": 8192},
    }

    def __init__(self, provider: str, model: str, agent_system_prompt: str = None, context: Context = None) -> None:
        """
        Initializes the CustomAgent with the given provider, model, system prompt, and context.

        Args:
            provider (str): The provider for the model.
            model (str): The model to be used.
            agent_system_prompt (str): The system prompt to initialize the context.
            context (Context, optional): An optional context object to maintain conversation history.
        """
        self.system_prompt = agent_system_prompt
        if context is None:
            self.context = Context()
            self.context.add_system_message(agent_system_prompt)
        else:
            self.context = context
        self.provider = provider
        self.model = model
        if self.model not in self.MODEL_PARAMS:
            raise ValueError(f"Model {self.model} is not supported.")
        
        self.max_tokens = self.MODEL_PARAMS[self.model]["max_tokens"]
  
    def change_model(self, new_provider: str, new_model: str):
        """
        Changes the model and provider used by the agent.

        Args:
            new_provider (str): The new provider for the model.
            new_model (str): The new model to be used.
        """
        self.provider = new_provider
        self.model = new_model
        self.max_tokens = self.MODEL_PARAMS[self.model]["max_tokens"]

    def chat_completion(self, user_prompt: str, stream: bool = False) -> Union[Callable[[], Generator[str, Any, None]], str]:
        """
        Generates a response to the user's prompt using memory and saving to it.

        Args:
            user_prompt (str): The user's prompt to generate a response for.
            stream (bool, optional): Whether to stream the response or not. Defaults to False.

        Returns:
            Union[Callable[[], Generator[str, Any, None]], str]: A function that yields chunks of the response if streaming, or the full response if not streaming.
        """
        self.context.add_user_message(user_prompt)
        
        def streaming_response() -> Generator[str, Any, None]:
            text = ""
            for chunk in modules.create_chat_completion(self.provider, self.model, self.context.to_list(), stream=True):
                text += chunk
                yield chunk
            self.context.add_assistant_message(text)
        
        if stream:
            return streaming_response()
        else:
            response = modules.create_chat_completion(self.provider, self.model, self.context.to_list())
            self.context.add_assistant_message(response)
            return self.context.get_last_message()

    def text_completion(self, user_prompt: str, system_prompt: str = None, stream: bool = False, use_context: bool = False) -> Union[Callable[[], Generator[str, Any, None]], str]:
        """
        Generates a one-shot response to the user's prompt, response will not be saved. Optionally uses the current context.

        Args:
            system_prompt (str): The system prompt to guide the response.
            user_prompt (str): The user's prompt to generate a response for.
            stream (bool, optional): Whether to stream the response or not. Defaults to False.
            use_context (bool, optional): Whether to use the current context or not. Defaults to False.

        Returns:
            Union[Callable[[], Generator[str, Any, None]], str]: A function that yields chunks of the response if streaming, or the full response if not streaming.
        """
        if use_context:
            combined_prompt = self.context.to_list()
            combined_prompt.append({"role": "user", "content": f"{user_prompt}"})
        elif system_prompt is not None:
            combined_prompt = [{"role": "system", "content": f"{system_prompt}"},{"role": "user", "content": f"{user_prompt}"}]
        else:
            combined_prompt = [{"role": "user", "content": f"{user_prompt}"}]
        
        def streaming_response() -> Generator[str, Any, None]:
            for chunk in modules.create_text_completion(self.provider, self.model, combined_prompt, stream=True):
                yield chunk
        
        if stream:
            return streaming_response()
        else:
            return modules.create_text_completion(self.provider, self.model, combined_prompt)



class Agents:
    class GroqMix():
        # TODO: 
        #     1. tweaking system prompts for better quality
        #     2. asinc requests 

        models = [
        ("llama3-70b-8192", "Groq"),
        ("mixtral-8x7b-32768", "Groq"),
        ("llama3-8b-8192", "Groq"),
        ("gemma-7b-it", "Groq"),
        ("gemma2-9b-it", "Groq")
        ]

        def __init__(self) -> None:
            self.worker_system_prompt = "You are a helpfull assistant"
            self.summarizer_system_prompt = "You are a summarizer model. Given a user's query and multiple responses from different LLM models, create the best combined response."
            self.context = Context()
            self.maxtokens = 8192

        def chat_completion(self, user_prompt: str, stream: bool = False) -> Union[Generator[str, Any, None], Context]:
            new_query = f"{user_prompt}\n"
            for model in self.models:
                response = modules.create_text_completion(model[1], model[0], self.worker_system_prompt, user_prompt, messages=self.context.to_list())
                new_query += f"Here is response from {model[0]}: '''{response}'''"
            response = modules.create_text_completion(self.models[0][1], self.models[0][0], self.summarizer_system_prompt, new_query, stream=stream)


            self.context.add_user_message(user_prompt)
            def streaming_response(generator) -> Generator[str, Any, None]:
                text = ''
                for chunk in generator:
                    text+= chunk
                    yield chunk
                self.context.add_assistant_message(text)

            if stream:
                return streaming_response()
            else:
                self.context.add_assistant_message(response)
                return response

                








if __name__ == "__main__":
    test = CustomAgent("YOU are an algorithm that outputs a python valid list of ints. nothing else", "llama3-8b-8192")
    print(test.send_request_return_type("how are you", list))