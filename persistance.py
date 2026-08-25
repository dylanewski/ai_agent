import json
from datetime import datetime
from prompts import system_prompt

HISTORY_FILE = "conversation_history.json"

def save_messages(old_sessions, current_messages, session_start, summary):
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

    data = {"summary": summary, "sessions": old_sessions + [current_session]}
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

COMPACT_THRESHOLD = 6   # compact when old sessions hold more than this many messages

def load_and_prepare(client):
    session_start = datetime.now().isoformat()

    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
        old_sessions = data.get("sessions", [])
        summary = data.get("summary", "")       
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        old_sessions = []
        summary = ""

    # if old sessions have grown too large, summarize them
    total_old_messages = sum(len(s["messages"]) for s in old_sessions)
    if total_old_messages > COMPACT_THRESHOLD:
        print(f"(Compacting {total_old_messages} old messages into a summary...)")
        messages_to_summarize = []
        for s in old_sessions:
            messages_to_summarize.extend(s["messages"])
        if summary:
            messages_to_summarize.insert(0, {"role": "system", "content": f"Previous summary: {summary}"})
        summary = summarize(client, messages_to_summarize)
        old_sessions = []    
        with open(HISTORY_FILE, "w") as f:
            json.dump({"summary": summary, "sessions": old_sessions}, f, indent=2)

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

    summary_prompt = """You are summarizing a conversation between a user and an AI coding agent. Produce a concise summary that preserves:
- Facts the user shared (preferences, personal details, decisions)
- Tasks that were accomplished (files created, code written, actions taken)
- Any ongoing context or unfinished work
- Keep the summary concise — a few short paragraphs at most, focusing only on the most important facts and outcomes.

Drop the chatty back-and-forth. Focus on what would be useful to remember going forward. Write it as a compact factual summary."""

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": f"Summarize this conversation:\n\n{conversation_text}"},
        ],
        temperature=0,      
    )
    return response.choices[0].message.content