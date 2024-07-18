import os
import shutil

def empty_folder(folder_path):
    if not os.path.exists(folder_path):
        raise ValueError(f"The folder path '{folder_path}' does not exist.")
    
    if not os.path.isdir(folder_path):
        raise ValueError(f"The path '{folder_path}' is not a directory.")
    
    # Iterate over the contents of the directory
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)  # Remove file or link
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)  # Remove directory and its contents