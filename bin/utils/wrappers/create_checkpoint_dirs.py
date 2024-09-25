#!/usr/bin/env python

import os
import re

def remove_file_extension(filename):
    while True:
        filename, ext = os.path.splitext(filename)
        if not ext:
            break
    return filename

def create_checkpoint_dirs(root_mappings_dir=None, root_registered_crops_dir=None, moving_image_path=None):
    filename = remove_file_extension(os.path.basename(moving_image_path))
    image_dirname = os.path.basename(os.path.dirname(moving_image_path))

    if root_mappings_dir is not None:
        current_mappings_dir = os.path.join(root_mappings_dir, image_dirname, filename)

        if not os.path.exists(current_mappings_dir):
            os.makedirs(current_mappings_dir, exist_ok=True)
    else: 
        current_mappings_dir = None

    if root_registered_crops_dir is not None:
        current_registered_crops_affine_dir = os.path.join(root_registered_crops_dir, 'affine', image_dirname, filename)
        current_registered_crops_diffeo_dir = os.path.join(root_registered_crops_dir, 'diffeomorphic', image_dirname, filename)

        if not os.path.exists(current_registered_crops_affine_dir):
            os.makedirs(current_registered_crops_affine_dir, exist_ok=True)

        if not os.path.exists(current_registered_crops_diffeo_dir):
            os.makedirs(current_registered_crops_diffeo_dir, exist_ok=True)
    else:
        root_registered_crops_dir = None

    return current_mappings_dir, current_registered_crops_affine_dir, current_registered_crops_diffeo_dir

def create_crops_dir(image_path, crops_dir):
    cycle_dir = os.path.basename(os.path.dirname(image_path))
    filename_dir = re.sub(r"\.\w+", "", os.path.basename(remove_file_extension(image_path)))
    crops_wd = os.path.join(crops_dir, cycle_dir, filename_dir)

    return crops_wd