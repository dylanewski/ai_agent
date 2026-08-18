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
            return f'Success: "{directory}" is within the working directory'
    except Exception as e:
        return f'Error: An unexpected error occurred - {str(e)}'
    