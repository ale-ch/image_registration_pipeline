#!/usr/bin/env python

import argparse
import os 
import gc
import logging
import re
from utils import logging_config
from utils.image_cropping import load_tiff_region
from utils.image_cropping import get_tiff_image_shape
from utils.image_cropping import get_padding_shape
from utils.image_cropping import zero_pad_array
from utils.image_cropping import get_crop_areas
from utils.image_cropping import crop_2d_array
from utils.pickle_utils import save_pickle, load_pickle
from skimage.io import imread
from utils.image_cropping import load_tiff_region
from utils.image_cropping import crop_2d_array_grid
from utils.image_cropping import zero_pad_arrays
from utils.wrappers.create_checkpoint_dirs import create_checkpoint_dirs
from utils.wrappers.compute_mappings import compute_mappings
from utils.wrappers.apply_mappings import apply_mappings
from utils.wrappers.export_image import export_image
from utils.empty_folder import empty_folder

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def save_image_crops(image, crop_areas, output_dir):
    """
    Loops through each crop area, processes the crop, and saves each crop individually.
    
    Args:
        image (ndarray): The input image (already padded if needed).
        crop_areas (tuple): Tuple containing crop indices and crop dimensions (from get_crop_areas).
        output_dir (str): Path to directory where crops will be saved (absolute path required ).
    """
    # Check directory to save the crops
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.debug(f'Directory created: {output_dir}')
    
    # Loop through each crop and save it
    for index, area in crop_areas:
        logger.debug(f'Processing crop_{index[0]}_{index[1]}')
        
        # Crop the image
        crop = (index, crop_2d_array(image, crop_areas=[area]))
        
        # Save each crop individually with a unique name
        crop_save_path = os.path.join(output_dir, f'crop_{index[0]}_{index[1]}.pkl')
        save_pickle(crop, crop_save_path)
        logger.debug(f'Saved crop_{index[0]}_{index[1]} to {crop_save_path}')

def elastic_registration(input_path, output_path, fixed_image_path, 
                    mappings_dir, crops_dir, registered_crops_dir, 
                    crop_width_x, crop_width_y, overlap_x, overlap_y, 
                    delete_checkpoints, max_workers):
    
    logger.info(f'Output path: {output_path}')
    
    # Check if output image directory exists 
    output_leaf_directory_path = os.path.dirname(output_path)
    if not os.path.exists(output_leaf_directory_path):
        os.makedirs(output_leaf_directory_path)
        logger.debug(f'Output directory created successfully: {output_leaf_directory_path}')
    
    current_mappings_dir, current_registered_crops_dir = create_checkpoint_dirs(mappings_dir, registered_crops_dir, input_path)

    mov_shape = get_tiff_image_shape(input_path)
    fixed_shape = get_tiff_image_shape(fixed_image_path)
    padding_shape = get_padding_shape(mov_shape, fixed_shape)
    crop_areas = get_crop_areas(shape=padding_shape, crop_width_x=crop_width_x, crop_width_y=crop_width_y, overlap_x=overlap_x, overlap_y=overlap_y)

    # Fixed image: load, pad to size and crop
    logger.debug(f"Loading fixed image {input_path}")
    fixed_image = imread(fixed_image_path)
    fixed_image = zero_pad_array(fixed_image, padding_shape)
    cycle_dir = os.path.basename(os.path.dirname(fixed_image_path))
    filename_dir = re.sub(r"\.\w+", "", os.path.basename(fixed_image_path))
    crops_dir_fixed = os.path.join(crops_dir, cycle_dir, filename_dir)
    save_image_crops(fixed_image, crop_areas, crops_dir_fixed)

    del fixed_image
    gc.collect()

    # Moving image: load, pad to size and crop
    logger.debug(f"Loading moving image {input_path}")
    moving_image  = imread(input_path)
    moving_image = zero_pad_array(moving_image, padding_shape)
    cycle_dir = os.path.basename(os.path.dirname(output_path))
    filename_dir = re.sub(r"\.\w+", "", os.path.basename(input_path))
    crops_dir_moving = os.path.join(crops_dir, cycle_dir, filename_dir)
    save_image_crops(moving_image, crop_areas, crops_dir_moving)
    
    del moving_image
    gc.collect()

    fixed_crops = []
    moving_crops = []
    for fixed_file, moving_file in zip(os.listdir(crops_dir_fixed), os.listdir(crops_dir_moving)):
        fixed_crop = load_pickle(fixed_file)
        moving_crop = load_pickle(moving_file)
        fixed_crops.append(fixed_crop)
        moving_crops.append(moving_crop)

    mappings = compute_mappings(fixed_crops, moving_crops, current_mappings_dir, max_workers)

    del fixed_crops
    gc.collect()

    registered_crops = apply_mappings(mappings=mappings, moving_crops=moving_crops, checkpoint_dir=current_registered_crops_dir)

    del moving_crops
    gc.collect()

    export_image(registered_crops=registered_crops, overlap_x=overlap_x, overlap_y=overlap_y, output_path=output_path)
    logger.info(f'Image {input_path} processed successfully.')

    empty_folder(crops_dir_moving)
    empty_folder(crops_dir_fixed)

    if delete_checkpoints:
        empty_folder(current_mappings_dir)
        logger.info(f'Content deleted successfully: {current_mappings_dir}')
        empty_folder(current_registered_crops_dir)
        logger.info(f'Content deleted successfully: {current_registered_crops_dir}')

def main(args):
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    elastic_registration(args.input_path, args.output_path, args.fixed_image_path,
                    args.mappings_dir, args.registered_crops_dir, 
                    args.crop_width_x, args.crop_width_y, 
                    args.overlap_x, args.overlap_y, 
                    args.delete_checkpoints, args.max_workers)

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
    parser.add_argument('--max-workers', type=int,
                        help='Maximum number of CPUs used by the process.')
    parser.add_argument('--delete-checkpoints', action='store_false', 
                        help='Delete image mappings and registered crops files after processing.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to directory where log files will be stored.')
    
    args = parser.parse_args()
    
    main(args)