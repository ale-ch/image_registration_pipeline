#!/usr/bin/env python

import argparse
import os 
import logging
from utils import logging_config
from utils.image_cropping import crop_image_channels
from utils.misc import create_checkpoint_dirs, get_crops_dir
from utils.wrappers.compute_mappings import compute_mappings
from utils.wrappers.apply_mappings import apply_mappings

# Set up logging configuration
logging_config.setup_logging()
logger = logging.getLogger(__name__)

def diffeomorphic_registration(current_crops_dir_fixed, current_crops_dir_moving, 
                               current_mappings_dir, current_registered_crops_dir, max_workers):
    """
    Performs diffeomorphic registration between fixed and moving image crops.

    Args:
        current_crops_dir_fixed (str): Directory containing fixed image crops.
        current_crops_dir_moving (str): Directory containing moving image crops.
        current_mappings_dir (str): Directory to save computed mappings.
        current_registered_crops_dir (str): Directory to save registered crops.
        max_workers (int): Maximum number of workers for parallel processing.
    """
    # List of files in each directory
    fixed_files = sorted([os.path.join(current_crops_dir_fixed, file) for file in os.listdir(current_crops_dir_fixed)])
    moving_files = sorted([os.path.join(current_crops_dir_moving, file) for file in os.listdir(current_crops_dir_moving)])

    # Filter the files that end with '2.pkl'
    fixed_files_dapi = [f for f in fixed_files if f.endswith('_2.pkl')]    
    moving_files_dapi = [f for f in moving_files if f.endswith('_2.pkl')]  
    
    # Compute mappings for all crop pairs
    compute_mappings(fixed_files_dapi, moving_files_dapi, current_crops_dir_fixed, current_crops_dir_moving, current_mappings_dir, max_workers)

    n_channels = 3
    mapping_files = sorted([os.path.join(current_mappings_dir, file) for file in os.listdir(current_mappings_dir)] * n_channels)
    apply_mappings(mapping_files, moving_files, current_registered_crops_dir, max_workers)


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
    output_path = os.path.join(args.output_dir, 'diffeomorphic', dirname, filename) # Path to output file

    if not os.path.exists(output_path):
        # Check if output image directory exists, create it if not
        output_dir_path = os.path.dirname(output_path)
        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)
            logger.debug(f'Output directory created successfully: {output_dir_path}')

        # Create intermediate directories for crops and mappings
        current_crops_dir_fixed = get_crops_dir(fixed_image_path, args.crops_dir_fixed)
        current_crops_dir_moving = get_crops_dir(input_path, args.crops_dir_moving)

        current_mappings_dir, current_registered_crops_dir, _ = create_checkpoint_dirs(
            root_mappings_dir=args.mappings_dir, 
            root_registered_crops_dir=args.registered_crops_dir, 
            moving_image_path=input_path,
            transformation='diffeomorphic'
        )

        # Crop images and save them to the crops directories
        crop_image_channels(input_path, fixed_image_path, current_crops_dir_fixed, 
                    args.crop_width_x, args.crop_width_y, args.overlap_x, args.overlap_y, which_crop='fixed')

        # Perform diffeomorphic registration
        diffeomorphic_registration(current_crops_dir_fixed, current_crops_dir_moving, current_mappings_dir, current_registered_crops_dir, args.max_workers)


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
                        help='Directory where image crops will be saved.')
    parser.add_argument('--crops-dir-moving', type=str, required=True,
                        help='Directory where image crops will be saved.')
    parser.add_argument('--mappings-dir', type=str, required=True, 
                        help='Root directory to save computed mappings.')
    parser.add_argument('--registered-crops-dir', type=str, required=True, 
                        help='Root directory to save registered crops.')
    parser.add_argument('--crop-width-x', required=True, type=int, 
                        help='Width of each crop.')
    parser.add_argument('--crop-width-y', required=True, type=int, 
                        help='Height of each crop.')
    parser.add_argument('--overlap-x', type=int, 
                        help='Overlap of each crop along the x-axis.')
    parser.add_argument('--overlap-y', type=int, 
                        help='Overlap of each crop along the y-axis.')
    parser.add_argument('--max-workers', type=int,
                        help='Maximum number of CPUs used for parallel processing.')
    parser.add_argument('--delete-checkpoints', action='store_false', 
                        help='Delete intermediate files after processing.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to the directory where log files will be stored.')
    
    args = parser.parse_args()
    
    main(args)
