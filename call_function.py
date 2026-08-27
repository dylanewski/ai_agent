import json
from collections.abc import Callable

from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.run_python_file import run_python_file, schema_run_python_file
from functions.write_file_content import schema_write_file_content, write_file


available_functions = [
    schema_get_files_info,
    schema_get_file_content,
    schema_run_python_file,
    schema_write_file_content,
]


def call_function(tool_call, verbose: bool = False, working_directory: str = "./ai_workspace"):
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments or "{}")
    function_args.update({"working_directory": working_directory})
    if verbose:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    function_map: dict[str, Callable[..., str]] = {
    "get_file_content": get_file_content,
    "get_files_info": get_files_info,
    "run_python_file": run_python_file,
    "write_file_content": write_file,
}
    if function_name in function_map:
        result = function_map[function_name](**function_args)
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        }
    else:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": f"Error: Unknown function: {function_name}",
        }