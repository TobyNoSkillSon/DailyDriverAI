from rich.syntax import Syntax
from rich.console import Console

def print_with_all_themes(code: str, language: str):
    themes = [
        "monokai", "dracula", "paraiso-dark", "solarized-dark", "monokai-sublime",
        "native", "friendly", "fruity", "lovelace", "algol", "algol_nu", "arduino", "rainbow_dash"
    ]
    console = Console()
    for theme in themes:
        console.print(f"[bold]Theme: {theme}[/bold]")
        syntax = Syntax(code, language, theme=theme, line_numbers=True)
        console.print(syntax)
        console.print("\n" + "="*80 + "\n")

# Example usage
code = '''def hello():
    print("Hello, World!")'''

print_with_all_themes(code, "python")
