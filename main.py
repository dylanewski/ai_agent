import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse
from prompts import system_prompt
from call_function import available_functions
from call_function import call_function
import json

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

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Smell ya later!")
            break
        messages.append({"role": "user", "content": user_input})

        for x in range(20):  # Limit to 20 iterations to prevent infinite loops
            response = generate_content(client, messages, temperature=args.temperature)
            if args.verbose:
                if response.usage is not None:
                    print(f"Prompt tokens: {response.usage.prompt_tokens}")
                    print(f"Response tokens: {response.usage.completion_tokens}")
                else:
                    print("Token usage information is not available in the response.")

            ai_message = response.choices[0].message
            messages.append(ai_message)

            if ai_message.tool_calls:
                for tool_call in ai_message.tool_calls:
                    result_message = call_function(tool_call, verbose=args.verbose, working_directory=working_dir)
                    if result_message['content'] == "":
                        result_message['content'] = "(the function returned no output)"
                    messages.append(result_message) 
                    if args.verbose:
                        print(f"-> {result_message['content']}")
            else:
                print(f"-> {ai_message.content}")
                break  # Exit the loop if no tool calls are present in the message
            print("\n---\n")  # Print a separator between iterations
        else:
            print("Agent did not finish its response within 20 iterations. Please check for potential issues.")
            

def validate_working_dir(path):
    resolved = os.path.abspath(path)          # resolve to true absolute path
    home = os.path.expanduser("~")
    forbidden = [os.path.abspath(os.sep), home]   # filesystem root and home dir

    if resolved in forbidden:
        print(f"Error: '{path}' resolves to a forbidden directory ({resolved}). Refusing to run.")
        exit(1)

    os.makedirs(resolved, exist_ok=True)      # create the workspace if it doesn't exist
    return resolved

def generate_content(client, messages, temperature=0.7):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        temperature=temperature,
        tools=available_functions
    )
    return response


if __name__ == "__main__":
    main()
