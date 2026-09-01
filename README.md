# AI Agent

A conversational AI coding agent that can work with files, run code, and search the web. It uses an LLM with function calling to plan and take actions in response to natural-language prompts, looping until it produces a final answer. The model can run either locally (via Ollama) or in the cloud (via OpenRouter), switchable in the config.

The agent has a persistent, time-aware memory that carries across runs, and can be used through either a browser-based chat interface or an interactive terminal session.

## How It Works

The agent runs in a loop. On each turn it sends the full conversation to the model, and the model either requests a function call or returns a final answer. When it requests a call, the agent executes the function, feeds the result back into the conversation, and loops again, iterating until the task is done. Conversations are saved to disk and reloaded on the next run, so the agent remembers previous sessions. When the conversation grows past a threshold, older messages are automatically summarized into a compact memory to keep context lean.

## Features

- **List files** — see file names, sizes, and directory status
- **Read files** — view file contents, truncated to a max length
- **Write files** — create or overwrite files
- **Run Python files** — execute a `.py` file with optional arguments and capture its output
- **Fetch web pages** — retrieve the readable text of any URL
- **Web search** — search the web for current information; pairs with page-fetching so the agent can find sources and then read them in full
- **Local or cloud model** — run the model on your own machine with Ollama, or in the cloud with OpenRouter, chosen with one config setting
- **Persistent memory** — conversations are saved across runs, organized into timestamped sessions the agent can reference
- **Automatic compaction** — once the conversation grows past a threshold, older history is summarized so context stays efficient
- **Two interfaces** — a browser-based chat UI and an interactive terminal session, both sharing the same agent core

File operations are restricted to a working directory (default `./ai_workspace`, created automatically), so the agent can't read or write outside of it. The web tools reach out to the internet and are not restricted to the working directory.

## Prerequisites

- [Python](https://www.python.org/) 3.13+
- [uv](https://docs.astral.sh/uv/) for dependency management and running the project
- **For the cloud model backend:** an [OpenRouter](https://openrouter.ai/) account and API key
- **For the local model backend:** [Ollama](https://ollama.com/) installed and running, with a model pulled (see below)
- A [Tavily](https://tavily.com/) API key for web search (free tier available)

You only need the OpenRouter key if you use the cloud backend, and only need Ollama if you use the local backend. Pick whichever you prefer; the web-search key is used either way.

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Create your `.env` file with your API keys. Copy the example and fill in your keys:

   ```bash
   cp .env.example .env
   ```

   ```
   OPENROUTER_API_KEY=your-openrouter-key-here
   TAVILY_API_KEY=your-tavily-key-here
   ```

   `.env` is git-ignored, so your keys stay local and never get committed. (The OpenRouter key can be left blank if you only use the local backend.)

3. Choose your model backend in `config.py`:

   ```python
   MODEL_BACKEND = "ollama"        # "ollama" (local) or "openrouter" (cloud)
   MODEL = "llama3.2"              # a pulled Ollama model, or an OpenRouter model name
   ```

### Running the model locally with Ollama

To use the local backend, install [Ollama](https://ollama.com/), make sure it's running, and pull a model:

```bash
ollama pull llama3.2
```

Then set `MODEL_BACKEND = "ollama"` and `MODEL = "llama3.2"` in `config.py`. The model runs entirely on your machine — no API costs, no internet needed for the model itself. Note that smaller local models are less precise about when to use tools than larger cloud models; if you find a local model over-eager or imprecise with tools, try a more capable one (such as `qwen2.5:7b`) or switch to the cloud backend.

## Usage

### Web interface

```bash
uv run app.py
```

Then open `http://localhost:5001` in your browser. Previous conversation history loads automatically, and the agent remembers context across messages and across runs.

### Terminal

```bash
uv run main.py
```

Type your messages at the prompt; type `quit` or `exit` to end the session.

Optional terminal flags:

- `--verbose` — print token usage and function-call details
- `--temperature <float>` — set the sampling temperature (default `0.7`)
- `--working-dir <path>` — the directory the agent is allowed to operate in (default `./ai_workspace`; refuses to run if pointed at `/` or your home directory)

## Project Structure

- `app.py` — Flask web server; serves the chat UI and handles chat and history requests
- `main.py` — terminal entry point; the interactive agent loop
- `agent.py` — the shared agent core (the tool-calling loop and model calls), used by both interfaces
- `call_function.py` — maps tool names to functions and executes the model's requested calls
- `persistence.py` — conversation persistence, session timestamps, and compaction
- `utils.py` — shared setup helpers (working-directory validation)
- `functions/` — the individual tool implementations (list, read, write, run, fetch, search)
- `prompts.py` — the system prompt that defines the agent's behavior and personality
- `config.py` — configuration values (model backend, model name, limits, thresholds, search settings)
- `templates/` — HTML for the web interface
- `static/` — CSS and JavaScript for the web interface
- `ai_workspace/` — the default sandbox the agent operates in (git-ignored)

## Web Search Provider

Web search is provided through Tavily by default, configured in `config.py` via `SEARCH_PROVIDER`. The search tool is structured so the provider can be swapped without changing the rest of the agent.

## Safety Notes

This agent can execute arbitrary Python code within its working directory, and can fetch arbitrary URLs and search the web. It is intended for learning and personal use on simple tasks. Keep the working directory scoped to a project you're comfortable with, and don't point it at sensitive directories.