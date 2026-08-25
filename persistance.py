import json
from datetime import datetime
from prompts import system_prompt

HISTORY_FILE = "conversation_history.json"

def save_messages(old_sessions, current_messages, session_start):
    serializable = []
    for m in current_messages:
        if hasattr(m, "model_dump"):
            full = m.model_dump()
            trimmed = {"role": full["role"], "content": full["content"]}
            if full.get("tool_calls"):
                trimmed["tool_calls"] = full["tool_calls"]
            serializable.append(trimmed)
        else:
            serializable.append(m)

    current_session = {
        "started": session_start,      
        "messages": serializable,
    }

    data = {"sessions": old_sessions + [current_session]}

    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_and_prepare():
    session_start = datetime.now().isoformat()          

    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
        old_sessions = data["sessions"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        old_sessions = []                               

    messages = [{"role": "system", "content": system_prompt}]

    # replay each past session, injecting a dated marker before its messages
    for session in old_sessions:
        readable = datetime.fromisoformat(session["started"]).strftime("%B %d, %Y at %I:%M %p")
        messages.append({"role": "system", "content": f"--- Session from {readable} ---"})
        messages.extend(session["messages"])

    # inject a marker for the CURRENT (new) session
    readable_now = datetime.fromisoformat(session_start).strftime("%B %d, %Y at %I:%M %p")
    messages.append({"role": "system", "content": f"--- Current session started {readable_now} ---"})

    return messages, old_sessions, session_start