import json

MAX_CHARS = 10000
WEB_MAX_CHARS = 5000

# ---- model backend ----
MODEL_BACKEND = "openrouter"
MODEL = "google/gemini-3.7-flash"
IMAGE_PROVIDER = "pollinations"


COMPACT_THRESHOLD = 100
SEARCH_PROVIDER = "tavily"
SEARCH_MAX_RESULTS = 5

_SETTINGS_FILE = "runtime_settings.json"


def _load_overrides():
    global MODEL, COMPACT_THRESHOLD
    try:
        with open(_SETTINGS_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return
    if isinstance(data.get("model"), str) and data["model"].strip():
        MODEL = data["model"].strip()
    if isinstance(data.get("compact_threshold"), int) and data["compact_threshold"] > 0:
        COMPACT_THRESHOLD = data["compact_threshold"]


def save_overrides():
    with open(_SETTINGS_FILE, "w") as f:
        json.dump({"model": MODEL, "compact_threshold": COMPACT_THRESHOLD}, f, indent=2)


_load_overrides()
