import os
from config import MAX_CHARS

def write_file(working_directory: str, file_path: str, content: str) -> str:
    absolute_path = os.path.abspath(working_directory)
    full_file_path = os.path.join(absolute_path, file_path)
    normalized_path = os.path.normpath(full_file_path)

    try:
        if not os.path.commonpath([absolute_path, normalized_path]) == absolute_path:
            return f"Error: Cannot write to '{file_path}' as it is outside the permitted working directory"
        if os.path.isdir(normalized_path):
            return f"Error: Cannot write to '{file_path}' as it is a directory"
        os.makedirs(os.path.dirname(normalized_path), exist_ok=True)
        with open(normalized_path, "w") as f:
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error writing file: {e}"