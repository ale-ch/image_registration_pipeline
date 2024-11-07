#!/usr/bin/env python

import argparse
import os 
import logging
import numpy as np
import re
import gc
from utils import logging_config
from utils.misc import create_checkpoint_dirs, make_io_paths
from utils.io import load_pickle, save_pickle
from utils.image_mapping import compute_diffeomorphic_mapping_dipy

# Set up logging configuration
logging_config.setup_logging()
logger = logging.getLogger(__name__)

def get_index_from_str(input_str):
    # Define the pattern to match
    pattern = r'\d+_\d+_\d+'
    
    # Find all the matches
    matches = re.findall(pattern, input_str)
    
    # If there are matches, return the last one
    if matches:
        return matches[-1]
    else:
        return None

def compute_mappings(crops_file, checkpoint_dir):
    """
    Loads a pair of fixed and moving crops from their respective directories,
    computes the diffeomorphic mapping if not already cached, and returns the mapping.

    Args:
        crops_file (str): Filename of the pickle file containing the the tuple (index, fixed crop, moving crop).
        checkpoint_dir (str): Directory to save/load checkpoint files.

    Returns:
        mapping_diffeomorphic: The computed or loaded diffeomorphic mapping, or None if shapes do not match.
    """
    pattern = re.compile(r'(\d+_\d+_\d+)\.pkl$')
    match = pattern.search(crops_file)
    idx = "_".join(match.group(0).split('_')[:-1]) # Get the first two indices

    # Construct the checkpoint path for storing/loading mappings
    # checkpoint_path = f'mapping_{idx}.pkl'
    checkpoint_path = os.path.join(checkpoint_dir, f'mapping_{idx}.pkl')

    if not os.path.exists(checkpoint_path):
        crops = load_pickle(crops_file)
        idx, fixed_crop, moving_crop = crops[0], crops[1], crops[2]

        del crops
        gc.collect()

        # Check for shape mismatch
        if fixed_crop[1].shape != moving_crop[1].shape:
            logger.error(f"Shape mismatch for crops at indices {idx}.")
            return None

        # Check for single valued crops (white areas)
        if len(np.unique(fixed_crop)) == 1 or len(np.unique(moving_crop)) == 1:
            mapping_diffeomorphic = 0
        else:
            # Compute the diffeomorphic mapping
            mapping_diffeomorphic = compute_diffeomorphic_mapping_dipy(fixed_crop, moving_crop)
        
        del fixed_crop, moving_crop
        gc.collect()
        
        # Save the computed mapping to a checkpoint
        save_pickle(mapping_diffeomorphic, checkpoint_path)
        logger.info(f"Saved checkpoint for i={idx}")

        del mapping_diffeomorphic
        gc.collect()
    
def main(args):
    # Set up logging to a file
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    input_path, output_path = make_io_paths(args.input_path, args.output_dir)

    # Get checkpoint directories
    current_mappings_dir, current_registered_crops_dir, _ = create_checkpoint_dirs(
            root_mappings_dir=args.mappings_dir, 
            root_registered_crops_dir=args.registered_crops_dir, 
            moving_image_path=input_path,
            transformation='diffeomorphic'
    )

    n_registered_crops = len(os.listdir(current_registered_crops_dir))
    n_mappings = len(os.listdir(current_mappings_dir))

    if not os.path.exists(output_path) or n_registered_crops != n_mappings:
        # Check if output image directory exists, create it if not
        output_dir_path = os.path.dirname(output_path)
        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)
            logger.debug(f'Output directory created successfully: {output_dir_path}')

        # Compute mappings
        compute_mappings(args.crops_path, current_mappings_dir)

if __name__ == "__main__":
    # Set up argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to the input (moving) image.')
    parser.add_argument('--output-dir', type=str, required=True, 
                        help='Path to save the registered image.')
    parser.add_argument('--crops-path', type=str, required=True, 
                        help='Path to pickle file containing the tuple (index, fixed crop, moving crop).')
    parser.add_argument('--mappings-dir', type=str, required=True, 
                        help='Root directory to save computed mappings.')
    parser.add_argument('--registered-crops-dir', type=str, required=True, 
                        help='Root directory to save registered crops.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to the directory where log files will be stored.')
    
    args = parser.parse_args()
    
    main(args)
