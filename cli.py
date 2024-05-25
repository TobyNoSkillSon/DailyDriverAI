from groq_interface import Groq_models
from context import Context

def model_selection(print_menu=True):
    if print_menu:
        print("""
Type the number to choose the model.
1. llama3-70b-8192
2. mixtral-8x7b-32768
3. llama3-7b-8192
4. gemma-7b-it
""")
    num = input("")
    match num:
        case "1":
            return "llama3-70b-8192"
        case "2":
            return "mixtral-8x7b-32768"
        case "3":
            return "llama3-7b-8192"  
        case "4":
            return "gemma-7b-it"
        case _:
            print("Invalid input. Please try again.")
            return model_selection(False)

system_prompt = "You are a helpful assistant!"
chat = Context()
model = 'llama3-70b-8192'
tools = False

print("""
Welcome to the CLI app!

\\system - lets you change the system prompt (standard assistant prompt)
\\model - lets you change the model (llama3 70B as a default)
\\clear - clears the context
\\tools - Toggle tool usage (Off by default)

or type whatever to get the response""")

while True:
    user_prompt = input("\n\n>>>")
    match user_prompt:
        case "\\system":
            system_prompt = input("Type your new system prompt: ")
            print(f"Your new system prompt is: '{system_prompt}'")
        case "\\model":
            model = model_selection()
            print(f"Your current model is: '{model}'")
        case "\\clear":
            chat = Context()
            print("Context cleared!")
        case "\\tools":
            tools = not tools
            print(f"Tools are set to: {tools}")
        case _:
            chat.add_user_message(user_prompt)
            chat = Groq_models().send_request(model, chat, tools)
