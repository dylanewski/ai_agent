AI Agent

A conversational AI coding agent that can list, read, write, and run files in a sandboxed working directory. It uses an LLM (via OpenRouter) with function calling to plan and take actions in response to natural-language prompts, looping until it produces a final answer.

The agent has a persistent, time-aware memory that carries across runs, and can be used through either a browser-based chat interface or an interactive terminal session.

How It Works

The agent runs in a loop. On each turn it sends the full conversation to the model, and the model either requests a function call or returns a final answer. When it requests a call, the agent executes the function, feeds the result back into the conversation, and loops again, iterating until the task is done. Conversations are saved to disk and reloaded on the next run, so the agent remembers previous sessions. When the conversation grows past a threshold, older messages are automatically summarized into a compact memory to keep context lean.

Features
List files — see file names, sizes, and directory status
Read files — view file contents, truncated to a max length
Write files — create or overwrite files
Run Python files — execute a .py file with optional arguments and capture its output
Persistent memory — conversations are saved across runs, organized into timestamped sessions the agent can reference
Automatic compaction — once the conversation grows past a threshold, older history is summarized so context stays efficient
Two interfaces — a browser-based chat UI and an interactive terminal session, both sharing the same agent core

All file operations are restricted to a working directory (default ./ai_workspace, created automatically), so the agent can't read or write outside of it.

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
Web interface

Start the web server:

bash
uv run app.py

Then open http://localhost:5001 in your browser. Type in the chat box and press Send (or Enter). Previous conversation history loads automatically when the page opens, and the agent remembers context across messages and across runs.

Terminal

For a terminal session instead:

bash
uv run main.py

Type your messages at the prompt. Type quit or exit to end the session.

Optional terminal flags:

--verbose — print token usage and function-call details
--temperature <float> — set the sampling temperature (default 0.7)
--working-dir <path> — the directory the agent is allowed to operate in (default ./ai_workspace, created automatically; refuses to run if pointed at / or your home directory)

Project Structure
app.py — Flask web server; serves the chat UI and handles chat and history requests
main.py — terminal entry point; the interactive agent loop
agent.py — the shared agent core (the tool-calling loop and model calls), used by both interfaces
call_function.py — maps tool names to functions and executes the model's requested calls
persistence.py — conversation persistence, session timestamps, and compaction
functions/ — the individual tool implementations (list, read, write, run)
prompts.py — the system prompt that defines the agent's behavior and personality
config.py — configuration values (model, limits, thresholds)
templates/ — HTML for the web interface
static/ — CSS and JavaScript for the web interface
ai_workspace/ — the default sandbox the agent operates in (git-ignored)
Safety Notes

This agent can execute arbitrary Python code within its working directory. It is intended for learning and personal use on simple tasks. Keep the working directory scoped to a project you're comfortable with, and don't point it at sensitive directories.