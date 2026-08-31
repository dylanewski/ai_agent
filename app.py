import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from config import COMPACT_THRESHOLD, MODEL_BACKEND
from agent import run_agent
from utils import validate_working_dir
from persistence import (
    load_and_prepare,
    save_messages,
    write_history,
    compact_if_needed,
)

load_dotenv()


def make_client():
    if MODEL_BACKEND == "ollama":
    
        try:
            requests.get("http://localhost:11434", timeout=2)
        except requests.exceptions.RequestException:
            raise RuntimeError(
                "Ollama backend selected but the server isn't reachable at "
                "localhost:11434. Make sure Ollama is running and you've pulled "
                "the model ('ollama pull llama3.2')."
            )
        return OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    else:  # openrouter
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if api_key is None:
            raise RuntimeError("OPENROUTER_API_KEY is not set in the environment variables.")
        return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)


client = make_client()

app = Flask(__name__)

# set up the working directory once, at startup (this doesn't change per request)
working_dir = validate_working_dir("./ai_workspace")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history")
def history():
    messages, _old, _start, _summary = load_and_prepare()

    clean = []
    for m in messages:
        role = m["role"] if isinstance(m, dict) else m.role
        content = m["content"] if isinstance(m, dict) else m.content
        if role == "user" and content:
            clean.append({"text": content, "sender": "user"})
        elif role == "assistant" and content:
            clean.append({"text": content, "sender": "agent"})

    return jsonify({"messages": clean})


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.get_json()["message"]

    # 1. LOAD the conversation fresh from the file
    messages, old_sessions, session_start, summary = load_and_prepare()
    session_start_index = len(messages)

    # 2. handle this one message
    messages.append({"role": "user", "content": user_message})
    reply = run_agent(client, messages, working_dir)

    current_new = messages[session_start_index:]
    final_sessions, final_summary = compact_if_needed(
        client, old_sessions, current_new, session_start, summary
    )
    write_history(final_sessions, final_summary)

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True, port=5001, exclude_patterns=["*/ai_workspace/*"])