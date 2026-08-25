# AI Agent

A simple AI coding agent that can list, read, write, and run files in a sandboxed working directory. It uses an LLM (via OpenRouter) with function calling to plan and take actions in response to a natural-language prompt, looping until it produces a final answer.

## Features

- **List files** — see file names, sizes, and directory status in the working directory (`get_files_info`)
- **Read files** — view file contents, truncated to a max length (`get_file_content`)
- **Write files** — create or overwrite files (`write_file`)
- **Run Python files** — execute a `.py` file with optional arguments and capture stdout/stderr (`run_python_file`)

All file operations are restricted to a working directory, so the agent can't read or write outside of it.

## Prerequisites

- [Python](https://www.python.org/) 3.13+
- [uv](https://docs.astral.sh/uv/) for dependency management and running the project
- An [OpenRouter](https://openrouter.ai/) account and API key

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Create your own `.env` file with your OpenRouter API key. Copy the example file and fill in your key:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env`:

   ```
   OPENROUTER_API_KEY=your-key-here
   ```

   `.env` is git-ignored, so your key stays local and never gets committed.

## Usage

Run the agent with a prompt:

```bash
uv run main.py "your prompt"
```

Optional flags:

- `--verbose` — print token usage and function call details
- `--temperature <float>` — set the sampling temperature (default `0.7`)

Example:

```bash
uv run main.py "list the files in the current directory" --verbose
```
