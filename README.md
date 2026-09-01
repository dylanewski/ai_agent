# AI Agent

A conversational AI coding agent that can work with files, run code, search the web, and generate and analyze images. It uses an LLM with function calling to plan and take actions in response to natural-language prompts, looping until it produces a final answer. The model can run either locally (via Ollama) or in the cloud (via OpenRouter), switchable in the config.

The agent has a persistent, time-aware memory that carries across runs, and can be used through either a browser-based chat interface or an interactive terminal session.

## How It Works

The agent runs in a loop. On each turn it sends the full conversation to the model, and the model either requests a function call or returns a final answer. When it requests a call, the agent executes the function, feeds the result back into the conversation, and loops again, iterating until the task is done. Conversations are saved to disk and reloaded on the next run, so the agent remembers previous sessions. When the conversation grows past a threshold, older messages are automatically summarized into a compact memory to keep context lean.

## Features

- **List files** — see file names, sizes, and directory status
- **Read files** — view file contents, truncated to a max length
- **Write files** — create or overwrite files
- **Run Python files** — execute a `.py` file with optional arguments and capture its output
- **Fetch web pages** — retrieve the readable text of any URL (cached briefly to avoid redundant fetches)
- **Web search** — search the web for current information (cached briefly to avoid redundant, metered API calls); pairs with page-fetching so the agent can find sources and then read them in full
- **Generate images** — create an image from a text description and display it in the chat
- **Analyze images** — describe or answer questions about an image, from a URL or an uploaded file, using a vision-capable model
- **Local or cloud model** — run the model on your own machine with Ollama, or in the cloud with OpenRouter, chosen with one config setting
- **Persistent memory** — conversations are saved across runs, organized into timestamped sessions the agent can reference
- **Automatic compaction** — once the conversation grows past a threshold, older history is summarized so context stays efficient
- **Two interfaces** — a browser-based chat UI and an interactive terminal session, both sharing the same agent core

File operations are restricted to a working directory (default `./ai_workspace`, created automatically), so the agent can't read or write outside of it. The web and image tools reach out to the internet and are not restricted to the working directory.

## Prerequisites

- [Python](https://www.python.org/) 3.13+
- [uv](https://docs.astral.sh/uv/) for dependency management and running the project
- **For the cloud model backend (and image analysis):** an [OpenRouter](https://openrouter.ai/) account and API key
- **For the local model backend:** [Ollama](https://ollama.com/) installed and running, with a model pulled
- A [Tavily](https://tavily.com/) API key for web search (free tier available)

Image generation uses a free, no-key service (Pollinations), so it needs no additional setup. Image analysis uses a vision-capable model through the cloud backend, so it requires the OpenRouter key and the cloud backend selected.

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

   `.env` is git-ignored, so your keys stay local and never get committed. (The OpenRouter key can be left blank if you only use the local backend and don't need image analysis.)

3. Choose your model backend in `config.py`:

   ```python
   MODEL_BACKEND = "openrouter"           # "ollama" (local) or "openrouter" (cloud)
   MODEL = "google/gemini-3.7-flash"      # a cloud model name, or a pulled Ollama model
   ```

### Running the model locally with Ollama

To use the local backend, install [Ollama](https://ollama.com/), make sure it's running, and pull a model:

```bash
ollama pull llama3.2
```

Then set `MODEL_BACKEND = "ollama"` and `MODEL` to your pulled model in `config.py`. The model runs entirely on your machine — no API costs, no internet needed for the model itself. Note that smaller local models are less reliable with tool use than cloud models; if a local model is imprecise with tools, try a more capable one or switch to the cloud backend. Image analysis requires the cloud backend, since it needs a vision-capable model.

## Usage

### Web interface

```bash
uv run app.py
```

Then open `http://localhost:5001` in your browser. Type a message and press Send (or Enter). Use the image button to upload a picture for the agent to analyze. Previous conversation history loads automatically, and the agent remembers context across messages and across runs.

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

- `app.py` — Flask web server; serves the chat UI and handles chat, history, image upload, and image analysis requests
- `main.py` — terminal entry point; the interactive agent loop
- `agent.py` — the shared agent core (the tool-calling loop and model calls), used by both interfaces
- `call_function.py` — maps tool names to functions and executes the model's requested calls
- `persistence.py` — conversation persistence, session timestamps, and compaction
- `utils.py` — shared setup helpers (working-directory validation)
- `functions/` — the individual tool implementations (list, read, write, run, fetch, search, generate image, analyze image)
- `prompts.py` — the system prompt that defines the agent's behavior and personality
- `config.py` — configuration values (model backend, model name, limits, thresholds, search and image settings)
- `templates/` — HTML for the web interface
- `static/` — CSS and JavaScript for the web interface
- `ai_workspace/` — the default sandbox the agent operates in (git-ignored)
- `uploaded_images/` — where uploaded images are stored (git-ignored)

## Web Search and Image Providers

Web search is provided through Tavily and image generation through Pollinations, both configured in `config.py` (`SEARCH_PROVIDER`, `IMAGE_PROVIDER`). Each is structured so the provider can be swapped without changing the rest of the agent.

## Safety Notes

This agent can execute arbitrary Python code within its working directory, and can fetch arbitrary URLs, search the web, and generate and analyze images. It is intended for learning and personal use on simple tasks. Keep the working directory scoped to a project you're comfortable with, and don't point it at sensitive directories.