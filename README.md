AI Agent

A conversational AI coding agent that can list, read, write, and run files in a sandboxed working directory. It uses an LLM (via OpenRouter) with function calling to plan and take actions in response to natural-language prompts, looping until it produces a final answer.

The agent runs as an interactive terminal session with persistent, time-aware memory across runs. A web interface is in progress.

How It Works

The agent runs in a loop. On each turn it sends the full conversation to the model, and the model either requests a function call or returns a final answer. When it requests a call, the agent executes the function, feeds the result back into the conversation, and loops again, iterating until the task is done. Conversations are saved to disk and reloaded on the next run, so the agent remembers previous sessions. When history grows large, it is automatically summarized to keep things efficient.

Features
List files — see file names, sizes, and directory status (get_files_info)
Read files — view file contents, truncated to a max length (get_file_content)
Write files — create or overwrite files (write_file)
Run Python files — execute a .py file with optional arguments and capture stdout/stderr (run_python_file)
Persistent memory — conversations are saved across runs, organized into timestamped sessions the agent can reference
Automatic compaction — older history is summarized once it grows past a threshold, keeping context lean

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

Usage (Terminal)

Start an interactive session:

bash
uv run main.py

Type your messages at the prompt. The agent remembers the conversation across turns and across runs. Type quit or exit to end the session.

Optional flags:

--verbose — print token usage and function-call details
--temperature <float> — set the sampling temperature (default 0.7)
--working-dir <path> — the directory the agent is allowed to operate in (default ./ai_workspace, created automatically; refuses to run if pointed at / or your home directory)
Web Interface (In Progress)

A browser-based chat interface is under development. It currently renders but is not yet wired up to the agent. To preview the interface:

bash
uv run app.py

Then open http://localhost:5000 in your browser. (On macOS, if port 5000 is taken by AirPlay, the app can be run on another port.)

Project Structure
main.py — terminal entry point; the interactive agent loop
app.py — Flask web server for the browser interface (in progress)
call_function.py — maps tool names to functions and executes the model's requested calls
persistance.py — conversation persistence, session timestamps, and compaction
functions/ — the individual tool implementations (list, read, write, run)
prompts.py — the system prompt that defines the agent's behavior and personality
config.py — configuration values (model, file-read limit)
templates/ — HTML for the web interface
static/ — CSS and JavaScript for the web interface
ai_workspace/ — the default sandbox the agent operates in (git-ignored)
Safety Notes

This agent can execute arbitrary Python code within its working directory. It is intended for learning and personal use on simple tasks. Keep the working directory scoped to a project you're comfortable with, and don't point it at sensitive directories.se on simple tasks. Keep the working directory scoped to a project you're comfortable with, and don't point it at sensitive directories
