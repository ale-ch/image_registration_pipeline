#!/usr/bin/env python

import os 
import pandas as pd
import logging
from skimage.io import imread 
from utils.image_cropping import estimate_overlap
from utils.image_cropping import crop_2d_array_grid
from utils.wrappers.create_checkpoint_dirs import create_checkpoint_dirs
from utils.wrappers.compute_mappings import compute_mappings
from utils.wrappers.apply_mappings import apply_mappings
from utils.wrappers.export_image import export_image
from utils.empty_folder import empty_folder
from utils import logging_config

import argparse

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def main(args):
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    with open('out_reg_py.txt', 'a+') as f:
        f.write('Input path: ' + str(args.input_path) + "\n")
        f.write('Output path: ' + str(args.output_path) + "\n")
        f.write('Fixed image path: ' + str(args.fixed_image_path) + "\n")
        f.write('Mappings dir: ' + str(args.mappings_dir) + "\n")
        f.write('Reg crops dir: ' + str(args.registered_crops_dir) + "\n")
        f.write('Crops width x: ' + str(args.crop_width_x) + "\n")
        f.write('Crops width y: ' + str(args.crop_width_y) + "\n")
        f.write('Overlap x: ' + str(args.overlap_x) + "\n")
        f.write('Overlap y: ' + str(args.overlap_y) + "\n")
        f.write('Auto-overlap: ' + str(args.auto_overlap) + "\n")
        f.write('Overlap factor: ' + str(args.overlap_factor) + "\n")
        f.write('Delete checkpoints: ' + str(args.delete_checkpoints) + "\n")
        f.write('Logs dir: ' + str(args.logs_dir) + "\n")

    logger.info(f'Output path: {args.output_path}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to input images.')
    parser.add_argument('--output-path', type=str, required=True, 
                        help='Path to registered image.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to fixed image')
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
    parser.add_argument('--auto-overlap', action='store_false', 
                        help='Automatically estimate overlap along both x and y axes.')
    parser.add_argument('--overlap-factor', type=float, 
                        help='Percentage by which the estimated overlap should be increased by.')
    parser.add_argument('--delete-checkpoints', action='store_false', 
                        help='Delete image mappings and registered crops files after processing.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to directory where log files will be stored.')
    args = parser.parse_args()
    
    main(args)