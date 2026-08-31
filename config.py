MAX_CHARS = 10000
WEB_MAX_CHARS = 5000

# ---- model backend ----
MODEL_BACKEND = "ollama"          # "ollama" (local) or "openrouter" (cloud)
MODEL = "llama3.2"                # used when MODEL_BACKEND is "ollama"
# MODEL = "openai/gpt-4o-mini"    # use this when MODEL_BACKEND is "openrouter"

COMPACT_THRESHOLD = 50
SEARCH_PROVIDER = "tavily"
SEARCH_MAX_RESULTS = 5