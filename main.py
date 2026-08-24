import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse
from prompts import system_prompt
from call_function import available_functions
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
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for response generation")
    args = parser.parse_args()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt}
    ]
    response = generate_content(client, messages, temperature=args.temperature)
    if args.verbose:
        if response.usage is not None:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")
        else:
            print("Token usage information is not available in the response.")

    message = response.choices[0].message
    if message.tool_calls:
        for tool_call in message.tool_calls:
            function_args = json.loads(tool_call.function.arguments or "{}") # type: ignore
            print(f"Calling function: {tool_call.function.name}({function_args})") # type: ignore
    else:
         print(f"Response:\n{message.content}")

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
