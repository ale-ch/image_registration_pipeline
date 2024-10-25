#!/usr/bin/env python

import os
import numpy as np
import logging
import re
import gc
from utils import logging_config
from concurrent.futures import ProcessPoolExecutor
from utils.io_tools import load_pickle, save_pickle
from utils.image_mapping import compute_diffeomorphic_mapping_dipy

# Setup logging configuration
logging_config.setup_logging()
logger = logging.getLogger(__name__)

def process_crop(fixed_file, moving_file, current_crops_dir_fixed, current_crops_dir_moving, checkpoint_dir):
    """
    Loads a pair of fixed and moving crops from their respective directories,
    computes the diffeomorphic mapping if not already cached, and returns the mapping.

    Args:
        fixed_file (str): Filename of the fixed crop.
        moving_file (str): Filename of the moving crop.
        current_crops_dir_fixed (str): Directory where fixed crops are stored.
        current_crops_dir_moving (str): Directory where moving crops are stored.
        checkpoint_dir (str): Directory to save/load checkpoint files.

    Returns:
        mapping_diffeomorphic: The computed or loaded diffeomorphic mapping, or None if shapes do not match.
    """
    match = re.search(r'\d+_\d+_\d+', fixed_file)
    idx = "_".join(match.group(0).split('_')[:-1]) # Get the first two indices

    # Construct the checkpoint path for storing/loading mappings
    checkpoint_path = os.path.join(checkpoint_dir, f'mapping_{idx}.pkl')
    if not os.path.exists(checkpoint_path):
        fixed_crop = load_pickle(os.path.join(current_crops_dir_fixed, fixed_file))
        moving_crop = load_pickle(os.path.join(current_crops_dir_moving, moving_file))  

        # Check for shape mismatch
        if fixed_crop[1].shape != moving_crop[1].shape:
            logger.error(f"Shape mismatch for crops at indices {idx}.")
            return None

        # Check for single valued crops (white areas)
        if len(np.unique(fixed_crop[1])) == 1 or len(np.unique(moving_crop[1])) == 1:
            mapping_diffeomorphic = 0
        else:
            # Compute the diffeomorphic mapping
            mapping_diffeomorphic = compute_diffeomorphic_mapping_dipy(fixed_crop[1], moving_crop[1])
        
        del fixed_crop, moving_crop
        gc.collect()
        
        # Save the computed mapping to a checkpoint
        save_pickle(mapping_diffeomorphic, checkpoint_path)
        logger.info(f"Saved checkpoint for i={idx}")

def compute_mappings(fixed_files, moving_files, current_crops_dir_fixed, current_crops_dir_moving, checkpoint_dir, max_workers=None):
    """
    Compute affine and diffeomorphic mappings between fixed and moving image crops in parallel.

    Parameters:
        fixed_files (list): List of filenames for the fixed crops.
        moving_files (list): List of filenames for the moving crops.
        current_crops_dir_fixed (str): Directory containing fixed crops.
        current_crops_dir_moving (str): Directory containing moving crops.
        checkpoint_dir (str): Directory to save/load checkpoint files.
        max_workers (int, optional): Maximum number of workers for parallel processing.

    Returns:
        list: List of mappings corresponding to each crop, or None for mismatched shapes.
    """
    if checkpoint_dir is not None:
        # Create checkpoint directory if it doesn't exist
        os.makedirs(checkpoint_dir, exist_ok=True)

    # Use ProcessPoolExecutor for parallel processing
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks for each crop to be processed in parallel
        for fixed_file, moving_file in zip(fixed_files, moving_files): 
            executor.submit(process_crop, fixed_file, moving_file, current_crops_dir_fixed, current_crops_dir_moving, checkpoint_dir)
    


