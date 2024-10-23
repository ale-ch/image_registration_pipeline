#!/usr/bin/env python

import argparse
import tifffile as tiff
import logging
import os
from utils.image_cropping import get_tiff_image_shape
from utils.image_cropping import get_padding_shape
from utils.image_cropping import remove_crops_overlap
from utils.image_stitching import stitch_crops
from utils.misc import create_checkpoint_dirs
from utils.misc import empty_folder
from utils import logging_config

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def export_image(input_path, output_path, fixed_image_path, overlap_x, overlap_y, max_workers, registered_crops_dir, registered_crops_no_overlap_dir):
    mov_shape = get_tiff_image_shape(input_path)  # Shape of moving image
    fixed_shape = get_tiff_image_shape(fixed_image_path)  # Shape of fixed image
    shape = get_padding_shape(mov_shape, fixed_shape)  # Calculate padding shape
    # Remove overlap from crops
    positions = remove_crops_overlap(registered_crops_dir, registered_crops_no_overlap_dir, 
                                    overlap_x, overlap_y, max_workers)
    # Stitch crops and export image
    stitched_image = stitch_crops(registered_crops_no_overlap_dir, shape, positions, max_workers)
    tiff.imwrite(output_path, stitched_image, imagej=True, metadata={'axes': 'ZYX'})
    logger.info(f'Image {input_path} processed successfully.')

def main(args):
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    if not os.path.exists(args.output_path):
        # Create checkpoint directories
        _, current_registered_crops_dir, current_registered_crops_no_overlap_dir = create_checkpoint_dirs(
            root_registered_crops_dir=args.registered_crops_dir, 
            moving_image_path=args.input_path,
            transformation=args.transformation
        )
    
        # Export image      
        export_image(args.input_path, args.output_path, args.fixed_image_path, args.overlap_x, args.overlap_y, args.max_workers,
                     current_registered_crops_dir, current_registered_crops_no_overlap_dir)

        # # Clear checkpoint directories if specified
        # if args.delete_checkpoints:
        #     empty_folder(current_registered_crops_dir)
        #     empty_folder(current_registered_crops_no_overlap_dir)
        #     logger.info(f'Directory {current_registered_crops_dir} emptied successfully.')

if __name__ == '__main__':
    # Set up argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to the input (moving) image.')
    parser.add_argument('--output-path', type=str, required=True, 
                        help='Path to save the registered image.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to the fixed image used for registration.')
    parser.add_argument('--registered-crops-dir', type=str, required=True, 
                        help='Directory to save intermediate registered crops.')
    parser.add_argument('--transformation', type=str, required=True,
                        help='Transformation that was applied to the registered crops. Either "affine" or "diffeomorphic".')
    parser.add_argument('--overlap-x', type=int, 
                        help='Overlap of each crop along the x-axis.')
    parser.add_argument('--overlap-y', type=int, 
                        help='Overlap of each crop along the y-axis.')
    parser.add_argument('--max-workers', type=int,
                        help='Maximum number of CPUs used for parallel processing.')
    # parser.add_argument('--delete-checkpoints', action='store_true', 
    #                     help='Delete intermediate files after processing.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to the directory where log files will be stored.')
    
    args = parser.parse_args()
    main(args)

