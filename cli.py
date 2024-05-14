from conversation import Groq_models
from context import Context

def model_selection(print_menu = True):
    if print_menu:
        print("""
Type the number to choose the model.
1. llama3-70b-8192
2. mixtral-8x7b-32768
3. llama3-7b-8192
4. llama2-70b-4096
5. gemma-7b-it
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
            return "llama2-70b-4096"
        case "5":
            return "gemma-7b-it"
        case _:
            print("Invalid input. Please try again.")
            return model_selection(False)



system_prompt = "You are a helpfull asistant!"
chat = Context() 
model = 'llama3-70b-8192'
tools = False

print("""
Weclcome to the cli app!
          
\\system - lets you change the system prompt (standard assistant prompt)
\\model - lets you change the model (lamma3 70B as a defalut)
\\clear - clears the context
\\tools - Togge tool usege (Off by defalut)

or type whatever to get the response""")


while True:
    user_prompt = input("\n\n\n")
    match user_prompt:
        case "\\system":
            system_prompt = input("Type your new system prompt: ")
            print(f"Your new system prompt is: '{system_prompt}'")
        case "\\model":
            model = model_selection()
            print(f"Your current model is: '{model}")
        case "\\clear":
            chat = Context()
            print("Context cleared!!")
        case "\\tools":
            if tools:
                tools = False
            else:
                tools = True
            print(f"Tools are set to: {tools}")
        case _:
            chat.add_user_message(user_prompt)
            chat = Groq_models().send_request(model, chat, tools)