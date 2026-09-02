import os
import uuid
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from openai import OpenAI
from config import COMPACT_THRESHOLD, MODEL_BACKEND
from agent import run_agent
from utils import validate_working_dir
from functions.analyze_image import analyze_image
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

# set up the working directory
working_dir = validate_working_dir("./ai_workspace")

# folder for uploaded images
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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


@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "no image provided"}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "no file selected"}), 400
    ext = os.path.splitext(secure_filename(file.filename))[1].lower()  # type: ignore
    if ext not in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
        return jsonify({"error": "unsupported file type"}), 400
    filename = f"{uuid.uuid4().hex}{ext}"
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({"url": f"/uploaded_images/{filename}"})


@app.route("/uploaded_images/<filename>")
def serve_uploaded_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    image_url = data["image_url"]
    question = data.get("question", "").strip()

    if question:
        prompt = question + " Respond in plain text only — no markdown, asterisks, bullets, or headers."
    else:
        prompt = "React briefly and casually to this image in a sentence or two, plain text only — no markdown or bullet points."

    local_path = image_url.lstrip("/")
    reply = analyze_image(local_path, prompt)

    # save the full exchange to history so it persists on reload
    messages, old_sessions, session_start, summary = load_and_prepare()
    session_start_index = len(messages)

    # user message: image + any typed text (matches the frontend display format)
    messages.append({"role": "user", "content": f"IMAGE: {image_url}"})
    if question:
        messages.append({"role": "user", "content": question})
    messages.append({"role": "assistant", "content": reply})

    current_new = messages[session_start_index:]
    final_sessions, final_summary = compact_if_needed(
        client, old_sessions, current_new, session_start, summary
    )
    write_history(final_sessions, final_summary)

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True, port=5001, exclude_patterns=["*/ai_workspace/*"])