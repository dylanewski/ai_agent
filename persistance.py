import json
from config import MAX_CHARS, MODEL
from datetime import datetime
from prompts import system_prompt

HISTORY_FILE = "conversation_history.json"
COMPACT_THRESHOLD = 50

def trim_messages(messages):
    serializable = []
    for m in messages:
        if hasattr(m, "model_dump"):
            full = m.model_dump()
            trimmed = {"role": full["role"], "content": full["content"]}
            if full.get("tool_calls"):
                trimmed["tool_calls"] = full["tool_calls"]
            serializable.append(trimmed)
        else:
            serializable.append(m)
    return serializable

def save_messages(old_sessions, current_messages, session_start, summary):
    serializable = trim_messages(current_messages)
    current_session = {"started": session_start, "messages": serializable}
    data = {"summary": summary, "sessions": old_sessions + [current_session]}
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_and_prepare():
    session_start = datetime.now().isoformat()

    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
        old_sessions = data.get("sessions", [])
        summary = data.get("summary", "")
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        old_sessions = []
        summary = ""

    messages = [{"role": "system", "content": system_prompt}]

    if summary:
        messages.append({"role": "system", "content": f"Summary of earlier conversations: {summary}"})

    for session in old_sessions:
        readable = datetime.fromisoformat(session["started"]).strftime("%B %d, %Y at %I:%M %p")
        messages.append({"role": "system", "content": f"--- Session from {readable} ---"})
        messages.extend(session["messages"])

    readable_now = datetime.fromisoformat(session_start).strftime("%B %d, %Y at %I:%M %p")
    messages.append({"role": "system", "content": f"--- Current session started {readable_now} ---"})

    return messages, old_sessions, session_start, summary

def summarize(client, messages_to_summarize):
    conversation_text = ""
    for m in messages_to_summarize:
        role = m.get("role", "unknown")
        content = m.get("content", "")
        if content:                          
            conversation_text += f"{role}: {content}\n"

        summary_prompt = """You are summarizing a conversation between a user and an AI coding agent. Produce a concise summary (a few short paragraphs at most) that preserves:
- Facts the user shared (preferences, personal details, decisions)
- Tasks that were accomplished (files created, code written, actions taken)
- Any ongoing or unfinished work

Prioritize recent information: preserve details from later in the conversation more fully, and compress or drop older details that are no longer relevant. If a previous summary is included, integrate it into a single cohesive summary rather than appending — consolidate overlapping points and let stale details fall away.

Drop the chatty back-and-forth. Focus on what would be useful to remember going forward."""

    response = client.chat.completions.create(
        model= MODEL,
        messages=[
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": f"Summarize this conversation:\n\n{conversation_text}"},
        ],
        temperature=0,      
    )
    return response.choices[0].message.content

def compact_if_needed(client, old_sessions, current_new, session_start, summary):
    current_session = {"started": session_start, "messages": trim_messages(current_new)}
    all_sessions = old_sessions + [current_session]

    total = sum(len(s["messages"]) for s in all_sessions)
    if total <= COMPACT_THRESHOLD:
        return all_sessions, summary     

    print(f"(Compacting {total} messages into a summary...)")
    messages_to_summarize = []
    if summary:
        messages_to_summarize.append({"role": "system", "content": f"Previous summary: {summary}"})
    for s in all_sessions:
        messages_to_summarize.extend(s["messages"])

    new_summary = summarize(client, messages_to_summarize)
    return [], new_summary       

def write_history(sessions, summary):
    data = {"summary": summary, "sessions": sessions}
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)