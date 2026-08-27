import os

def validate_working_dir(path):
    resolved = os.path.abspath(path)         
    home = os.path.expanduser("~")
    forbidden = [os.path.abspath(os.sep), home]   

    if resolved in forbidden:
        print(f"Error: '{path}' resolves to a forbidden directory ({resolved}). Refusing to run.")
        exit(1)

    os.makedirs(resolved, exist_ok=True)     
    return resolved