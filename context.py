import json
import os
from datetime import datetime

class Context:
    '''This class provides an easy way to create a context chain and store it in a JSON file'''
    def __init__(self, filename: str = None) -> None:
        if filename is None:
            now = datetime.now()
            filename = now.strftime("%Y-%m-%d-%H-%M-%S.json")
        self.filename = os.path.join("chat_logs", filename)
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.messages = json.load(f)
        else:
            self.messages = []
            self.save()

    def to_list(self):
        return list(self.messages)

    def save(self) -> None:
        with open(self.filename, 'w') as f:
            json.dump(self.messages, f, indent=4)

    def add_system_message(self, prompt:str) -> None: 
        self.messages.insert(0, {"role": "system", "content": f"{prompt}"})
        self.save()

    def add_user_message(self, prompt: str) -> None:
        self.messages.append({"role": "user", "content": f"{prompt}"})
        self.save()

    def add_assistant_message(self, response: str) -> None:
        self.messages.append({"role": "assistant", "content": f"{response}"})
        self.save()

    def delete_last_message(self, num: int = 1) -> None:
        for _ in range(num):
            self.messages.pop()
        self.save()

    def get_last_message(self) -> dict[str, str]:
        """{"role": "assistant", "content": f"{response}"}"""
        return self.messages[-1]

    def modify_last_message(self, new_content: str) -> None:
        self.messages[-1]["content"] = new_content
        self.save()
    
    def modify_system_message(self, prompt: str) -> None:
        self.messages.pop(0)
        self.add_system_message(prompt)
    
    def add_tool_message(self, tool_call_id, function_name, function_response) -> None:
        # they fixed it :D
        self.messages.append(
            {
                "tool_call_id": tool_call_id,
                "role": "tool",
                "name": function_name,
                "content": function_response
             })
        self.save()
