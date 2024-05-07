
from dotenv import load_dotenv
from context import Context
from groq import Groq
import tools
import json
import os



user_prompt = "What was the score of the Warriors game?"
print(run_conversation(user_prompt))