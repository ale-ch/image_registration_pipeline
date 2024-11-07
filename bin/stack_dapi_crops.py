#!/usr/bin/env python

import argparse
import os 
import logging
import numpy as np
import gc
from utils.io import load_pickle, save_pickle
from utils import logging_config
from utils.image_cropping import crop_image_channels
from utils.misc import get_crops_dir

# Set up logging configuration
logging_config.setup_logging()
logger = logging.getLogger(__name__)

def stack_dapi_crops(input_path, current_crops_dir_fixed, current_crops_dir_moving):
        """
        Performs diffeomorphic registration between fixed and moving image crops.

        Args:
            current_crops_dir_fixed (str): Directory containing fixed image crops.
            current_crops_dir_moving (str): Directory containing moving image crops.
        """
        # List of files in each directory
        fixed_files = sorted([os.path.join(current_crops_dir_fixed, file) for file in os.listdir(current_crops_dir_fixed)])
        moving_files = sorted([os.path.join(current_crops_dir_moving, file) for file in os.listdir(current_crops_dir_moving)])

        # Filter the files that end with '2.pkl'
        fixed_files_dapi = [f for f in fixed_files if f.endswith('_2.pkl')]    
        moving_files_dapi = [f for f in moving_files if f.endswith('_2.pkl')]

        whole_slide_id = os.path.basename(input_path).split('.')[0]

        for fixed_file, moving_file in zip(fixed_files_dapi, moving_files_dapi):
            fixed = load_pickle(fixed_file)
            moving = load_pickle(moving_file)

            idx, fixed = fixed[0], fixed[1]
            _, moving = moving[0], moving[1]

            crop_id = f'{whole_slide_id}_{idx[0]}_{idx[1]}_{idx[2]}'

            save_pickle((idx, fixed, moving), f"{crop_id}.pkl")

            del fixed, moving
            gc.collect()

def main(args):
    # Set up logging to a file
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    input_path = args.input_path.replace('.nd2', '.h5')
    fixed_image_path = args.fixed_image_path.replace('.nd2', '.h5')

    filename = os.path.basename(input_path) # Name of the output file 
    dirname = os.path.basename(os.path.dirname(input_path)) # Name of the parent directory to output file
    input_path = os.path.join(args.output_dir, 'affine', dirname, filename) # Path to input file

    # Create intermediate directories for crops
    current_crops_dir_fixed = get_crops_dir(fixed_image_path, args.crops_dir_fixed)
    current_crops_dir_moving = get_crops_dir(input_path, args.crops_dir_moving)

    # Crop images and save them to the crops directories
    crop_image_channels(input_path, fixed_image_path, current_crops_dir_fixed, 
                args.crop_width_x, args.crop_width_y, args.overlap_x, args.overlap_y, which_crop='fixed')

    stack_dapi_crops(input_path, current_crops_dir_fixed, current_crops_dir_moving)

if __name__ == "__main__":
    # Set up argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to the input (moving) image.')
    parser.add_argument('--output-dir', type=str, required=True, 
                        help='Path to save the registered image.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to the fixed image used for registration.')
    parser.add_argument('--crops-dir-fixed', type=str, required=True,
                        help='Directory where fixed image crops will be saved.')
    parser.add_argument('--crops-dir-moving', type=str, required=True,
                        help='Directory where moving image crops will be saved.')
    parser.add_argument('--crop-width-x', required=True, type=int, 
                        help='Width of each crop.')
    parser.add_argument('--crop-width-y', required=True, type=int, 
                        help='Height of each crop.')
    parser.add_argument('--overlap-x', type=int, 
                        help='Overlap of each crop along the x-axis.')
    parser.add_argument('--overlap-y', type=int, 
                        help='Overlap of each crop along the y-axis.')
    parser.add_argument('--delete-checkpoints', action='store_false', 
                        help='Delete intermediate files after processing.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to the directory where log files will be stored.')
    
    args = parser.parse_args()
    
    main(args)
