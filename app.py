import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

from agent import run_agent
from persistence import load_and_prepare, save_messages
from utils import validate_working_dir


load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")
if api_key is None:
    raise RuntimeError("OPENROUTER_API_KEY is not set in the environment variables.")

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

app = Flask(__name__)

working_dir = validate_working_dir("./ai_workspace")
messages, old_sessions, session_start, summary = load_and_prepare()
session_start_index = len(messages)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data["message"]

    messages.append({"role": "user", "content": user_message})

    reply = run_agent(client, messages, working_dir)

    current_new = messages[session_start_index:]
    save_messages(old_sessions, current_new, session_start, summary)

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True, port=5001)