import os
import re 

def match_pattern_str_list(pattern: str, str_list: list):
    """
    Match a pattern in a list of strings.
    
    Parameters:
        pattern (str): The regex pattern to match.
        str_list (list): List of strings to search.

    Returns:
        matches (list): List of match objects where the pattern was found.
    """
    matches = [re.search(pattern, f) for f in str_list]
    return matches

def make_paths_from_matches(dir_path, matches):
    """
    Create full paths from match objects.
    
    Parameters:
        dir_path (str): The directory path.
        matches (list): List of match objects.

    Returns:
        paths (list): List of full paths for the matched files.
    """
    if not os.path.isdir(dir_path):
        raise ValueError(f"{dir_path} is not a valid directory.")
    
    paths = [os.path.join(dir_path, match.string) for match in matches if match]
    return paths

def get_fixed_image_path(files_paths: list, pattern: str='CYCLE_1'):
    """
    Get the fixed image path and moving images paths.
    
    Parameters:
        files_paths (list): List of file paths.
        pattern (str, optional): Pattern to identify the fixed image. Default is 'CYCLE_1'.

    Returns:
        fixed_image_path (str): Path to the fixed image.
        moving_images_paths (list): List of paths to the moving images.
    """
    fixed_image_path = [path for path in files_paths if pattern in path][0]
    moving_images_paths = [path for path in files_paths if path != fixed_image_path]

    return fixed_image_path, moving_images_paths

def get_leaf_directory(file_path): 
    return os.path.basename(os.path.dirname(file_path))

def filter_elements(patterns, elements):
    matched_elements = []
    for element in elements:
        if any(re.search(pattern, element) for pattern in patterns):
            matched_elements.append(element)
    return matched_elements

def read_paths_from_file(file_path):
    """
    Read paths from a file.
    
    Parameters:
        file_path (str): Path to the file containing the paths.

    Returns:
        list: List of paths read from the file.
    """
    if not os.path.isfile(file_path):
        raise ValueError(f"{file_path} is not a valid file path.")
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return []
