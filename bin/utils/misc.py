#!/usr/bin/env python

import os
import re
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

def get_indexed_filepaths(registered_crops_dir):
    crops_filenames = os.listdir(registered_crops_dir)
    crops_paths = sorted([os.path.join(registered_crops_dir, file) for file in crops_filenames])
    indices = sorted([tuple(map(int, re.search(r'\d+_\d+_\d+', filename).group(0).split('_'))) for filename in crops_filenames])
    
    crops_paths = [(idx, path) for idx, path in zip(indices, crops_paths)]

    return crops_paths

def remove_file_extension(filename):
    """
    Recursively remove all file extensions from a given filename.

    Args:
        filename (str): The filename from which to remove extensions.

    Returns:
        str: The filename without any extensions.
    """
    while True:
        filename, ext = os.path.splitext(filename)
        if not ext:  # Exit if there are no more extensions
            break
    return filename

def create_checkpoint_dirs(root_mappings_dir=None, root_registered_crops_dir=None, moving_image_path=None, transformation=''):
    """
    Create directories for storing mappings and registered crops based on the moving image path.

    Args:
        root_mappings_dir (str): Root directory for storing mappings.
        root_registered_crops_dir (str): Root directory for storing registered crops.
        moving_image_path (str): Path to the moving image.

    Returns:
        tuple: Paths for the current mappings directory, affine crops directory, 
               and diffeomorphic crops directory.
    """
    # Extract filename and image directory name from the moving image path
    filename = remove_file_extension(os.path.basename(moving_image_path))
    image_dirname = os.path.basename(os.path.dirname(moving_image_path))

    # Initialize mapping directory
    if root_mappings_dir is not None:
        current_mappings_dir = os.path.join(root_mappings_dir, image_dirname, filename)

        # Create the mappings directory if it does not exist
        os.makedirs(current_mappings_dir, exist_ok=True)
    else: 
        current_mappings_dir = None

    # Initialize registered crops directories
    if root_registered_crops_dir is not None:

        current_registered_crops_dir = os.path.join(root_registered_crops_dir, transformation, image_dirname, filename)
        current_registered_crops_no_overlap_dir = os.path.join(root_registered_crops_dir, transformation, 'no_overlap', image_dirname, filename)

        os.makedirs(current_registered_crops_dir, exist_ok=True)
        os.makedirs(current_registered_crops_no_overlap_dir, exist_ok=True)
    else:
        current_registered_crops_dir = None
        current_registered_crops_no_overlap_dir = None

    return current_mappings_dir, current_registered_crops_dir, current_registered_crops_no_overlap_dir

def get_crops_dir(image_path, crops_dir):
    """
    Create a directory path for storing image crops based on the given image path.

    Args:
        image_path (str): Path to the original image.
        crops_dir (str): Base directory for storing crops.

    Returns:
        str: The constructed directory path for storing crops.
    """
    # Get the cycle directory name and filename without extension
    cycle_dir = os.path.basename(os.path.dirname(image_path))
    filename_dir = re.sub(r"\.\w+", "", os.path.basename(remove_file_extension(image_path)))
    
    # Construct the full crops directory path
    crops_wd = os.path.join(crops_dir, cycle_dir, filename_dir)

    return crops_wd
