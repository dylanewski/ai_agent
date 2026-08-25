AI Agent

A simple AI coding agent that can list, read, write, and run files in a sandboxed working directory. It uses an LLM (via OpenRouter) with function calling to plan and take actions in response to a natural-language prompt, looping until it produces a final answer.

How It Works

The agent runs in a loop. On each turn it sends the full conversation to the model, and the model either requests a function call or returns a final answer. When it requests a call, the agent executes the function, feeds the result back into the conversation, and loops again, iterating until the task is done or a maximum number of steps is reached.

Features
List files — see file names, sizes, and directory status in the working directory (get_files_info)
Read files — view file contents, truncated to a max length (get_file_content)
Write files — create or overwrite files (write_file)
Run Python files — execute a .py file with optional arguments and capture stdout/stderr (run_python_file)

All file operations are restricted to a working directory (default ./ai_workspace, created automatically on first run), so the agent can't read or write outside of it. You can point it at a different directory with the --working-dir flag, and the agent refuses to run if that directory resolves to your filesystem root or home directory.

Prerequisites
Python 3.13+
uv for dependency management and running the project
An OpenRouter account and API key
Setup
Install dependencies:
bash
   uv sync
Create your own .env file with your OpenRouter API key. Copy the example file and fill in your key:
bash
   cp .env.example .env

Then edit .env:

   OPENROUTER_API_KEY=your-key-here

.env is git-ignored, so your key stays local and never gets committed.

Usage

Run the agent with a prompt:

bash
uv run main.py "your prompt"

Optional flags:

--verbose — print token usage and function call details
--temperature <float> — set the sampling temperature (default 0.7)
--working-dir <path> — the directory the agent is allowed to operate in (default ./ai_workspace, created automatically; refuses to run if pointed at / or your home directory)

Example:

bash
uv run main.py "list the files in the current directory" --verbose
bash
uv run main.py "create a file called notes.txt with a haiku about the ocean"
Project Structure
main.py — entry point; parses arguments, runs the agent loop
call_function.py — maps tool names to functions and executes the model's requested calls
functions/ — the individual tool implementations (list, read, write, run)
prompts.py — the system prompt that instructs the agent
config.py — configuration values (e.g. the file-read character limit)
ai_workspace/ — the default sandbox the agent operates in (git-ignored)
Safety Notes

This agent can execute arbitrary Python code within its working directory. It is intended for learning and personal use on simple tasks. Keep the working directory scoped to a project you're comfortable with, and don't point it at sensitive directories
