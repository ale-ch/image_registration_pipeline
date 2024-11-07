#!/usr/bin/env python

import argparse
import logging
import os
import numpy as np
import re
import gc
from utils import logging_config
from utils.misc import create_checkpoint_dirs, get_crops_dir, make_io_paths
from utils.io import save_pickle, load_pickle
from utils.image_mapping import apply_mapping
from concurrent.futures import ProcessPoolExecutor

# Set up logging configuration
logging_config.setup_logging()
logger = logging.getLogger(__name__)

def process_crop(mapping_file, moving_file, checkpoint_dir=None):
    """
    Apply affine and diffeomorphic mappings to a set of image crops and save/load results from checkpoints.

    Parameters:
        mapping_file (list): Path to diffeomorphic mapping file.
        moving_file (list): Path to moving crop file.
        checkpoint_dir (str): Directory to save/load checkpoint files.
    """
    pattern = re.compile(r'(\d+_\d+_\d+)\.pkl$')
    match = pattern.search(mapping_file)
    idx = "_".join(match.group(0).split('_')[:-1]) # Get the first two indices

    checkpoint_path = os.path.join(checkpoint_dir, f'registered_split_{idx}.pkl')
    if not os.path.exists(checkpoint_path):
        moving_crop = load_pickle(moving_file)
        mapping = load_pickle(mapping_file)

        # Check for single valued array (such as white border)
        if not len(np.unique(moving_crop[1])) == 1:
        # Apply mappings
            save_pickle((moving_crop[0], apply_mapping(mapping, moving_crop[1], method='dipy')), checkpoint_path)
        else:
        # Return crop as is
            save_pickle(moving_crop[0], moving_crop[1])

        print(f"Saved checkpoint for i={moving_crop[0]}")
        
        del moving_crop, mapping
        gc.collect()        

def apply_mappings(mapping_files, moving_files, checkpoint_dir, max_workers=None):
    """
    Compute affine and diffeomorphic mappings between fixed and moving image crops in parallel.

    Parameters:
        mapping_files (list): List of filenames for the mapping.
        moving_files (list): List of filenames for the moving crops.
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
        for moving_file, mapping_file,  in zip(moving_files, mapping_files):
            executor.submit(process_crop, mapping_file, moving_file, checkpoint_dir)

def main(args):
    # Set up logging to a file
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    input_path, _ = make_io_paths(args.input_path, args.output_dir)

    # Get checkpoint directories
    current_mappings_dir, current_registered_crops_dir, _ = create_checkpoint_dirs(
            root_mappings_dir=args.mappings_dir, 
            root_registered_crops_dir=args.registered_crops_dir, 
            moving_image_path=input_path,
            transformation='diffeomorphic'
    )

    # Create intermediate directories for crops and mappings
    current_crops_dir_moving = get_crops_dir(input_path, args.crops_dir_moving)

    n_channels = 3
    mapping_files = sorted([os.path.join(current_mappings_dir, file) for file in os.listdir(current_mappings_dir)] * n_channels)
    moving_files = sorted([os.path.join(current_crops_dir_moving, file) for file in os.listdir(current_crops_dir_moving)])
    apply_mappings(mapping_files, moving_files, current_registered_crops_dir, args.max_workers)

if __name__ == "__main__":
    # Set up argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to the input (moving) image.')
    parser.add_argument('--output-dir', type=str, required=True, 
                        help='Path to save the registered image.')
    parser.add_argument('--crops-dir-moving', type=str, required=True,
                        help='Directory where image crops will be saved.')
    parser.add_argument('--mappings-dir', type=str, required=True, 
                        help='Root directory to save computed mappings.')
    parser.add_argument('--registered-crops-dir', type=str, required=True, 
                        help='Root directory to save registered crops.')
    parser.add_argument('--max-workers', type=int,
                        help='Maximum number of CPUs used for parallel processing.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to the directory where log files will be stored.')
    
    args = parser.parse_args()
    
    main(args)