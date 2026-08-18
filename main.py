import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse

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
    {"role": "user", "content": args.user_prompt},
]
    response = generate_content(client, messages, temperature=args.temperature)
    if args.verbose:
        if response.usage is not None:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")
        else:
            print("Token usage information is not available in the response.")

    print(f"Response:\n{response.choices[0].message.content}")

def generate_content(client, messages, temperature=0.7):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        temperature=temperature
    )
    return response
if __name__ == "__main__":
    main()
