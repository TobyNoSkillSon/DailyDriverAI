from context import Context
from agents import CustomAgent

def main_menu():
    print("""
Welcome to the CLI app!

\\system - lets you change the system prompt (standard assistant prompt)
\\model - lets you change the model (llama3 70B as a default)
\\clear - clears the context
\\tools - Toggle tool usage (Off by default)

or type whatever to get the response""")
    return

def model_selection(print_menu=True):
    if print_menu:
        print("""
Type the number to choose the model.
1. llama3-70b-8192     Groq
2. mixtral-8x7b-32768  Groq
3. llama3-7b-8192      Groq
4. gemma-7b-it         Groq
5. gpt-4o              OpenAI
6. gpt-3.5-turbo       OpenAI
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
        case "5":
            return "gpt-4o"
        case "6":
            return "gpt-3.5-turbo"
        case _:
            print("Invalid input. Please try again.")
            return model_selection(False)



system_prompt = "You are a helpful assistant!"
model = 'llama3-70b-8192'
tools = False
agent_instance =  CustomAgent(system_prompt, model)

main_menu()
while True:
    user_prompt = input("\n\n>>>")
    match user_prompt:
        case "\\system":
            system_prompt = input("Type your new system prompt: ")
            agent_instance.context.modify_system_message(system_prompt)
            print(f"Your new system prompt is: '{system_prompt}'")

        case "\\model":
            model = model_selection()
            agent_instance.change_model(model)
            print(f"Your current model is: '{model}'")
        case "\\clear":
            agent_instance.context = Context()
            agent_instance.context.add_system_message(system_prompt)
            print("Context cleared!")
        case "\\tools":
            tools = not tools
            print(f"Tools are set to: {tools}")
        case _:
            for chunk in agent_instance.send_request(user_prompt, True):
                print(chunk, end="")
            