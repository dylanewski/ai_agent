import argparse
import os

from dotenv import load_dotenv
from openai import OpenAI

from agent import run_agent
from persistence import save_messages, load_and_prepare, write_history, compact_if_needed
from utils import validate_working_dir


load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")
if api_key is None:
    raise RuntimeError("OPENROUTER_API_KEY is not set in the environment variables.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--working-dir", type=str, default="./ai_workspace", help="The directory the agent is allowed to operate in")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for response generation")
    args = parser.parse_args()
    working_dir = validate_working_dir(args.working_dir)

    messages, old_sessions, session_start, summary = load_and_prepare()
    session_start_index = len(messages)  

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("\nClosing session...\n")
            current_new = messages[session_start_index:]
            final_sessions, final_summary = compact_if_needed(
                client, old_sessions, current_new, session_start, summary
            )
            write_history(final_sessions, final_summary)
            break

        messages.append({"role": "user", "content": user_input})

        reply = run_agent(client, messages, working_dir, temperature=args.temperature, verbose=args.verbose)
        print(f"\nAi: {reply}")

        current_new = messages[session_start_index:]
        save_messages(old_sessions, current_new, session_start, summary)
            


if __name__ == "__main__":
    main()
