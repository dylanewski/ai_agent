import os


def get_files_info(working_directory: str, directory: str = ".") -> str:
    absolute_path = os.path.abspath(working_directory)
    directory_path = os.path.join(absolute_path, directory)
    normalized_path = os.path.normpath(directory_path)

    try:
        path_check = os.path.commonpath([absolute_path, normalized_path]) == absolute_path
        if not path_check:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(normalized_path):
            return f'Error: "{directory}" is not a directory'
        else:
            container = []
            for i in os.listdir(normalized_path):
                item_path = os.path.join(normalized_path, i)
                container.append(f'- {i}: file_size={os.path.getsize(item_path)} bytes, is_dir={os.path.isdir(item_path)}')
            return "\n".join(container)

    except Exception as e:
        return f'Error: An unexpected error occurred - {str(e)}'

schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
                    },
                },
            },
        },
    }


