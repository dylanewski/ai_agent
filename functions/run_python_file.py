import os
import subprocess
from config import MAX_CHARS

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    absolute_path = os.path.abspath(working_directory)
    full_file_path = os.path.join(absolute_path, file_path)
    normalized_path = os.path.normpath(full_file_path)

    try:
        path_check = os.path.commonpath([absolute_path, normalized_path]) == absolute_path
        if not path_check:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(normalized_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not normalized_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        else:
            command = ["python", normalized_path]
            if args:
                command.extend(args)
            result = subprocess.run(command, cwd=absolute_path, timeout=30, capture_output=True, text=True)

            if result.stdout == "" and result.stderr == "":
                return "No output produced"

            output = ""
            if result.stdout != "":
                output += f"STDOUT: {result.stdout}"
            if result.stderr != "":
                output += f"STDERR: {result.stderr}"
            if result.returncode != 0:
                output += f"Process exited with code {result.returncode}"

            return output
    except Exception as e:
        return f'Error: An unexpected error occurred - {str(e)}'

schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Executes a Python file in the specified directory with given arguments",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the Python file to execute, relative to the working directory",
                },
                "args": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Arguments to pass to the Python file",
                }
            },
        },
    }
}