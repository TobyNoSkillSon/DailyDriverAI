from context import Context
from agents import CustomAgent, Agents
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich import print as rprint
from rich.prompt import Prompt
import os
console = Console()

def get_multiline_input():
    console = Console()
    lines = []
    console.print("\n\n[bold green]>>>[/] ", end= "")
    while True:
        line = Prompt.ask("")
        if line == "" and lines[-1] == "":
            break
        lines.append(line)
    return "\n".join(lines[:-1])


def main_menu():
    menu = """
Welcome to the CLI app!

\\system - lets you change the system prompt (standard assistant prompt)
\\model - lets you change the model (llama3 70B as a default)
\\clear - clears the context
\\tools - Toggle tool usage (Off by default)

or type whatever to get the response
    """
    console.print(Panel(menu, title="Main Menu", border_style="cyan"))

def model_selection(print_menu=True):
    if print_menu:
        models = """
Type the number to choose the model.
1. llama3-70b-8192     Groq        
2. mixtral-8x7b-32768  Groq     
3. llama3-8b-8192      Groq
4. gemma-7b-it         Groq
5. gpt-4o              OpenAI
6. gpt-3.5-turbo       OpenAI
7. mixtral-8x7B        TogetherAI
8. claude 3 opus       Anthropic
9. claude 3.5 sonnet   Anthropic
10.claude 3 haiku      Anthropic
11.Qwen2-72B Instruct  TogetherAI
12.Gemma2 9b           Groq
        """
        console.print(Panel(models, title="Model Selection", border_style="green"))
    
    num = console.input("[bold cyan]Enter model number: [/]")
    models = {
        "1": ("llama3-70b-8192", "Groq"),
        "2": ("mixtral-8x7b-32768", "Groq"),
        "3": ("llama3-8b-8192", "Groq"),
        "4": ("gemma-7b-it", "Groq"),
        "5": ("gpt-4o", "OpenAI"),
        "6": ("gpt-3.5-turbo", "OpenAI"),
        "7": ("mistralai/Mixtral-8x7B-Instruct-v0.1", "TogetherAI"),
        "8": ("claude-3-opus-20240229", "Anthropic"),
        "9": ("claude-3-5-sonnet-20240620", "Anthropic"),
        "10": ("claude-3-haiku-20240307", "Anthropic"),
        "11": ("Qwen/Qwen2-72B-Instruct", "TogetherAI"),
        "12": ("gemma2-9b-it", "Groq")
    }
    
    if num in models:
        return models[num]
    else:
        console.print("[bold red]Invalid input. Please try again.[/]")
        return model_selection(False)


def main():
    system_prompt = "You are helpfull assistant"
    model, provider = "llama3-70b-8192", "Groq"
    agent_instance = Agents.GroqMix()               #CustomAgent(provider, model, system_prompt)
    tools = False
    stream = False

    main_menu()
    while True:
        user_prompt =  console.input("\n\n[bold green]>>>[/] ")  #get_multiline_input()
        match user_prompt:
            case "\\system":
                system_prompt = console.input("[bold yellow]Type your new system prompt: [/]")
                agent_instance.context.modify_system_message(system_prompt)
                console.print(f"[bold yellow]Your new system prompt is:[/] '{system_prompt}'")

            case "\\model":
                model, provider = model_selection()
                agent_instance.change_model(provider, model)
                console.print(f"[bold green]Your current model is:[/] '{model}' [bold green]from provider:[/] '{provider}'")
            case "\\clear":
                agent_instance.context = Context()
                agent_instance.context.add_system_message(system_prompt)
                if os.name == 'nt':
                    os.system('cls')
                else:
                    os.system('clear')
                main_menu()
                console.print("[bold green]Context cleared![/]")
            case "\\tools":
                tools = not tools
                console.print(f"[bold green]Tools are set to:[/] {tools}")
            case _:
                console.print("\n[bold blue]Assistant:[/]")
                if stream:
                    with console.status("[bold yellow]Thinking...[/]"):
                        for chunk in agent_instance.chat_completion(user_prompt, stream):
                            print(chunk, end="")
                else:
                    with console.status("[bold yellow]Thinking...[/]"):
                        response = agent_instance.chat_completion(user_prompt, stream)
                    
                    # Split the response into parts
                    parts = response.split("```")
                    for i, part in enumerate(parts):
                        if i % 2 == 0:  # Not a code block
                            console.print(Markdown(part))
                        else:  # Code block
                            lines = part.split('\n')
                            language = lines[0].strip() if lines[0].strip() else "python"
                            code = '\n'.join(lines[1:]) if lines[0].strip() else part
                            syntax = Syntax(code, language, theme="monokai",)
                            console.print(syntax)

if __name__ == "__main__":
    main()