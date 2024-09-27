#!/usr/bin/env python

import argparse
import os 
import logging
from utils import logging_config
from utils.pickle_utils import load_pickle
from utils.image_cropping import crop_images
from utils.wrappers.create_checkpoint_dirs import create_checkpoint_dirs, create_crops_dir
from utils.wrappers.compute_mappings import compute_mappings
from utils.wrappers.apply_mappings import apply_mappings
from utils.wrappers.export_image import export_image
from utils.empty_folder import empty_folder

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
    fixed_files = [os.path.join(current_crops_dir_fixed, file) for file in os.listdir(current_crops_dir_fixed)]
    moving_files = [os.path.join(current_crops_dir_moving, file) for file in os.listdir(current_crops_dir_moving)]
    
    # Compute mappings for all crop pairs
    mappings = compute_mappings(fixed_files, moving_files, current_crops_dir_fixed, current_crops_dir_moving, current_mappings_dir, max_workers)

    # Load moving crops from their directory
    moving_crops = []
    for file in moving_files:
        moving_crops.append(load_pickle(file))

    # Apply the computed mappings to the moving crops
    apply_mappings(mappings=mappings, moving_crops=moving_crops, checkpoint_dir=current_registered_crops_dir)

def main(args):
    # Set up logging to a file
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info(f'Input path: {args.input_path}')
    logger.info(f'Output path: {args.output_path}')
    
    # Check if output image directory exists, create it if not
    output_dir_path = os.path.dirname(args.output_path)
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
        logger.debug(f'Output directory created successfully: {output_dir_path}')

    # Create intermediate directories for crops and mappings
    current_crops_dir_fixed = create_crops_dir(args.fixed_image_path, args.crops_dir)
    current_crops_dir_moving = create_crops_dir(args.input_path, args.crops_dir)
    current_mappings_dir, _, current_registered_crops_dir = create_checkpoint_dirs(args.mappings_dir, args.registered_crops_dir, args.input_path)

    # Crop images and save them to the crops directories
    crop_images(args.input_path, args.fixed_image_path, current_crops_dir_fixed, current_crops_dir_moving, 
                args.crop_width_x, args.crop_width_y, args.overlap_x, args.overlap_y)

    # Perform diffeomorphic registration
    diffeomorphic_registration(current_crops_dir_fixed, current_crops_dir_moving, current_mappings_dir, current_registered_crops_dir, args.max_workers)
    
    # Load registered crops
    registered_crops = []
    for file in os.listdir(current_registered_crops_dir):
        filepath = os.path.join(current_registered_crops_dir, file)
        registered_crop = load_pickle(filepath)
        registered_crops.append(registered_crop)
    
    # Stitch crops and export the full registered image
    export_image(registered_crops, args.overlap_x, args.overlap_y, args.output_path)
    logger.info(f'Image {args.input_path} processed successfully.')
    
    # Clear checkpoint directories if specified
    if args.delete_checkpoints:
        empty_folder(current_crops_dir_fixed)
        empty_folder(current_crops_dir_moving)
        empty_folder(current_mappings_dir)
        empty_folder(current_registered_crops_dir)

if __name__ == "__main__":
    # Set up argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to the input (moving) image.')
    parser.add_argument('--output-path', type=str, required=True, 
                        help='Path to save the registered image.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to the fixed image used for registration.')
    parser.add_argument('--crops-dir', type=str, required=True,
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
