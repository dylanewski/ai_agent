import os
from config import MAX_CHARS


def get_file_content(working_directory: str, file_path: str) -> str:
    absolute_path = os.path.abspath(working_directory)
    full_file_path = os.path.join(absolute_path, file_path)
    normalized_path = os.path.normpath(full_file_path)

    try:
        path_check = os.path.commonpath([absolute_path, normalized_path]) == absolute_path
        if not path_check:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(normalized_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        else:
            with open(normalized_path, 'r') as f:
                file_content_string = f.read(MAX_CHARS)
                if f.read(1):
                    file_content_string += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            return file_content_string
    except Exception as e:
        return f'Error: An unexpected error occurred - {str(e)}'

schema_get_file_content = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": "Retrieves the content of a specified file relative to the working directory, truncated to a maximum number of characters",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read, relative to the working directory",
                },
            },
            "required": ["file_path"],
        },
    }
}