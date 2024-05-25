# DailyDriverAI 🚀

DailyDriverAI is a CLI application that allows you to communicate with large language models (LLMs) such as llama3 and gemma. The application also supports tools, with more tools currently under development. 💡

## Features

- Communicate with various LLMs. 💬
- Change system prompts and models on the fly. 🔄
- Maintain conversation context and store it in JSON files. 💾
- Toggle tool usage. ⚙️

## Usage

Run the CLI application:

```bash
python cli.py
```

### Available Commands

- \system - Change the system prompt. 🛠️
- \model - Change the model (default is llama3-70b-8192). 🤖
- \clear - Clear the current context. 🧹
- \tools - Toggle tool usage (default is off). 🛠️

### Example

Welcome to the CLI app! 🎉

\system - Change the system prompt 🔄
\model - Change the model (default is llama3-70b-8192) 🤖
\clear - Clear the context 🧹
\tools - Toggle tool usage (Off by default) 🛠️

or type a message to get a response 💬

## Code Overview

### Main Application

The main application logic is in main.py, providing the CLI interface and interacting with the language models. 📝

### Context Management

The Context class in context.py manages conversation context, storing messages in a JSON file. 💼

### Tools Support

This app supports tools, and more are currently being developed. Stay tuned for updates! ⚙️

## Setup

To use this app, you need to provide your own Groq API key. Create a .env file in the root directory of the project and add your Groq API key:

GROQ_API_KEY=your_api_key_here 🗝️

This version is more concise, written in Markdown with added emojis to enhance readability and engagement. Adjust as needed for your specific repository.
