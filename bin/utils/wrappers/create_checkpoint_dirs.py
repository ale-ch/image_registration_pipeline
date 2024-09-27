#!/usr/bin/env python

import os
import re

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

def create_checkpoint_dirs(root_mappings_dir=None, root_registered_crops_dir=None, moving_image_path=None):
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
        current_registered_crops_affine_dir = os.path.join(root_registered_crops_dir, 'affine', image_dirname, filename)
        current_registered_crops_diffeo_dir = os.path.join(root_registered_crops_dir, 'diffeomorphic', image_dirname, filename)

        # Create affine crops directory
        os.makedirs(current_registered_crops_affine_dir, exist_ok=True)

        # Create diffeomorphic crops directory
        os.makedirs(current_registered_crops_diffeo_dir, exist_ok=True)
    else:
        current_registered_crops_affine_dir = None
        current_registered_crops_diffeo_dir = None

    return current_mappings_dir, current_registered_crops_affine_dir, current_registered_crops_diffeo_dir

def create_crops_dir(image_path, crops_dir):
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
