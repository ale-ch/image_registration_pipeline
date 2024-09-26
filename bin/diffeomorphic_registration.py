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

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def diffeomorphic_registration(current_crops_dir_fixed, current_crops_dir_moving, 
                               current_mappings_dir, current_registered_crops_dir, max_workers):
    # List of files in each directory
    fixed_files = [os.path.join(current_crops_dir_fixed, file) for file in os.listdir(current_crops_dir_fixed)]
    moving_files = [os.path.join(current_crops_dir_moving, file) for file in os.listdir(current_crops_dir_moving)]
    
    # Parallel loading of crops
    mappings = compute_mappings(fixed_files, moving_files, current_crops_dir_fixed, current_crops_dir_moving, current_mappings_dir, max_workers)

    moving_crops = []
    for file in moving_files:
        moving_crops.append(load_pickle(file))

    apply_mappings(mappings=mappings, moving_crops=moving_crops, checkpoint_dir=current_registered_crops_dir)

def main(args):
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info(f'Input path: {args.input_path}')
    logger.info(f'Output path: {args.output_path}')
    
    # Check if output image directory exists 
    output_dir_path = os.path.dirname(args.output_path)
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
        logger.debug(f'Output directory created successfully: {output_dir_path}')

    # Create intermediate directories
    current_crops_dir_fixed = create_crops_dir(args.fixed_image_path, args.crops_dir)
    current_crops_dir_moving = create_crops_dir(args.input_path, args.crops_dir)
    current_mappings_dir, _ , current_registered_crops_dir = create_checkpoint_dirs(args.mappings_dir, args.registered_crops_dir, args.input_path)

    # Crop images and save them to crops directories
    crop_images(args.input_path, args.fixed_image_path, current_crops_dir_fixed, current_crops_dir_moving, 
                args.crop_width_x, args.crop_width_y, args.overlap_x, args.overlap_y)

    # Compute diffeomorphic mappings
    diffeomorphic_registration(current_crops_dir_fixed, current_crops_dir_fixed, current_mappings_dir, current_registered_crops_dir, args.max_workers)
    
    
    # Load registered crops
    registered_crops = []
    for file in os.listdir(current_registered_crops_dir):
        filepath = os.path.join(current_registered_crops_dir, file)
        registered_crop = load_pickle(filepath)
        registered_crops.append(registered_crop)
    
    # Stitch crops and export the full image
    export_image(registered_crops, args.overlap_x, args.overlap_y, args.output_path)
    logger.info(f'Image {args.input_path} processed successfully.')
    
    # # Clear checkpoint directories
    if args.delete_checkpoints:
        empty_folder(current_crops_dir_fixed)
        empty_folder(current_crops_dir_fixed)
        empty_folder(current_mappings_dir)
        empty_folder(current_registered_crops_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to input images.')
    parser.add_argument('--output-path', type=str, required=True, 
                        help='Path to registered image.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to fixed image')
    parser.add_argument('--crops-dir', type=str, required=True,
                        help='Directory where image crops will be saved')
    parser.add_argument('--mappings-dir', type=str, required=True, 
                        help='Root directory to save mappings.')
    parser.add_argument('--registered-crops-dir', type=str, required=True, 
                        help='Root directory to save registered crops.')
    parser.add_argument('--crop-width-x', required=True, type=int, 
                        help='Crop width.')
    parser.add_argument('--crop-width-y', required=True, type=int, 
                        help='Crop height.')
    parser.add_argument('--overlap-x', type=int, 
                        help='Overlap of each crop along x axis.')
    parser.add_argument('--overlap-y', type=int, 
                        help='Overlap of each crop along y axis.')
    parser.add_argument('--max-workers', type=int,
                        help='Maximum number of CPUs used by the process.')
    parser.add_argument('--delete-checkpoints', action='store_false', 
                        help='Delete image mappings and registered crops files after processing.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to directory where log files will be stored.')
    
    args = parser.parse_args()
    
    main(args)
