#!/usr/bin/env python

import os
import logging
from utils import logging_config
from concurrent.futures import ProcessPoolExecutor
from utils.pickle_utils import load_pickle, save_pickle
from utils.image_mapping import compute_diffeomorphic_mapping_dipy

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def process_crop(fixed_file, moving_file, current_crops_dir_fixed, current_crops_dir_moving, checkpoint_dir):
    """
    Loads a pair of fixed and moving crops from their respective directories.

    Args:
        fixed_file (str): Filename of the fixed crop.
        moving_file (str): Filename of the moving crop.
        current_crops_dir_fixed (str): Directory where fixed crops are stored.
        current_crops_dir_moving (str): Directory where moving crops are stored.

    Returns:
        tuple: A tuple containing the fixed crop and the moving crop.
    """
    fixed_crop = load_pickle(os.path.join(current_crops_dir_fixed, fixed_file))
    moving_crop = load_pickle(os.path.join(current_crops_dir_moving, moving_file))

    checkpoint_path = os.path.join(checkpoint_dir, f'mapping_{fixed_crop[0][0]}_{fixed_crop[0][1]}.pkl')
    
    if os.path.exists(checkpoint_path):
        # Load mapping from checkpoint if it exists
        mapping_diffeomorphic = load_pickle(checkpoint_path)
        print(f"Loaded checkpoint for i={fixed_crop[0][0]}_{fixed_crop[0][1]}")
    else:
        fixed_crop_dapi = fixed_crop[1][:, :, 2]
        mov_crop_dapi = moving_crop[1][:, :, 2]

        if fixed_crop_dapi.shape != mov_crop_dapi.shape:
            return None
        else:
            mapping_diffeomorphic = compute_diffeomorphic_mapping_dipy(fixed_crop_dapi, mov_crop_dapi)
            # Save the computed mapping
            save_pickle(mapping_diffeomorphic, checkpoint_path)
            print(f"Saved checkpoint for i={fixed_crop[0][0]}_{fixed_crop[0][1]}")
            
    return mapping_diffeomorphic

def compute_mappings(fixed_files, moving_files, current_crops_dir_fixed, current_crops_dir_moving, checkpoint_dir, max_workers=None):
    """
    Compute affine and diffeomorphic mappings between fixed and moving image crops in parallel.

    Parameters:
        fixed_crops (list): List of tuples containing crop indices and fixed image data.
        moving_crops (list): List of tuples containing crop indices and moving image data.
        checkpoint_dir (str): Directory to save/load checkpoint files.
        max_workers (int, optional): Maximum number of workers to use for parallel processing.

    Returns:
        list: List of mappings corresponding to each crop.
    """
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)

    mappings = []

    # Use ProcessPoolExecutor for parallel processing
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks for each crop
        futures = [
            executor.submit(process_crop, fixed_file, moving_file, current_crops_dir_fixed, current_crops_dir_moving, checkpoint_dir)
            for fixed_file, moving_file in zip(fixed_files, moving_files)
        ]

        # Collect the results as they complete
        for future in futures:
            # print(len(future.result()))
            # print(future.result())
            # print(future.result()[1])
            # mappings.append(future.result()["mapping"])
            mappings.append(future.result())

    return mappings