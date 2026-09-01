from call_function import call_function, available_functions
from config import MODEL


def run_agent(client, messages, working_dir, temperature=0.7, verbose=False):
    for _ in range(20):  # cap iterations to prevent infinite loops
        response = generate_content(client, messages, temperature=temperature)

        if verbose and response.usage is not None:
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")

        ai_message = response.choices[0].message
        messages.append(ai_message)  # type: ignore

        if ai_message.tool_calls:
            for tool_call in ai_message.tool_calls:
                result_message = call_function(tool_call, verbose=verbose, working_directory=working_dir)
                if result_message["content"] == "":
                    result_message["content"] = "(the function returned no output)"

                # if a tool produced an image, return it directly —
                # don't let the model rewrite the IMAGE: URL into prose
                if result_message["content"].startswith("IMAGE:"):
                    return result_message["content"]

                messages.append(result_message)
                if verbose:
                    print(f"-> {result_message['content']}")
        else:
            return ai_message.content
        
def generate_content(client, messages, temperature=0.7):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        tools=available_functions
    )
    return response