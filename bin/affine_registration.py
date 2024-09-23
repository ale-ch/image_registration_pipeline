#!/usr/bin/env python

import numpy as np
import gc
import argparse
import logging
import os
from utils import logging_config
from skimage.io import imread
from utils.image_cropping import load_tiff_region
from utils.image_cropping import zero_pad_arrays
from utils.image_cropping import crop_2d_array_grid
from utils.image_cropping import get_crop_areas
from utils.image_mapping import compute_affine_mapping_cv2
from utils.wrappers.apply_mappings import apply_mappings
from utils.wrappers.export_image import export_image

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def get_cropping_params(image):
    shape = image.shape
    
    if shape[0] > 64000: # cv2.warpAffine() is limited to images of size 32767x32767
        crop_fraction_y = 3
    else:
        crop_fraction_y = 2
    
    if shape[1] > 64000:
        crop_fraction_x = 3
    else:
        crop_fraction_x = 2
    
    crop_width_y = shape[0] // crop_fraction_y
    crop_width_x = shape[1] // crop_fraction_x
    overlap_y = int(crop_width_y // 1.5)
    overlap_x = int(crop_width_x // 1.5)

    return crop_width_x, crop_width_y, overlap_x, overlap_y

def get_dense_crop(moving, fixed, crop_width_x, crop_width_y, overlap_x, overlap_y):
    shape = moving.shape
    crop_areas = get_crop_areas(shape=shape, crop_width_x=crop_width_x, crop_width_y=crop_width_y, overlap_x=overlap_x, overlap_y=overlap_y)[1]
    for area in crop_areas:
        fixed_crop = fixed[area[0]:area[1], area[2]:area[3], :]
        moving_crop = moving[area[0]:area[1], area[2]:area[3], :]
    
        # Compute percentage of zero-valued pixels in image
        moving_crop_dapi_scaled = (moving_crop[:,:,2] - np.min(moving_crop[:,:,2]))
        zero_prop = (moving_crop_dapi_scaled.size - np.count_nonzero(moving_crop_dapi_scaled)) / moving_crop_dapi_scaled.size
    
        del moving_crop_dapi_scaled
        gc.collect()
    
        if zero_prop <= 0.3:
            break

    return fixed_crop, moving_crop

def affine_registration(input_path, output_path, fixed_image_path, crop=True, crop_size=4000, n_features=2000):
    logger.info(f'Output path: {output_path}')

    # Check if output image directory exists 
    leaf_directory_path = os.path.basename(os.path.dirname(output_path))
    if not os.path.exists(leaf_directory_path):
        os.makedirs(leaf_directory_path)
        logger.debug(f'Output directory created successfully: {leaf_directory_path}')

    logger.debug(f"Loading fixed image {input_path}")
    fixed_image = imread(fixed_image_path) # [10000:30000, 10000:30000, :]
    logger.debug(f"Loading moving image {input_path}")
    moving_image  = imread(input_path) # [8000:28000, 10000:30000, :]

    logger.debug(f'Moving image shape: {moving_image.shape}')
    logger.debug(f'Fixed image shape: {fixed_image.shape}')

    if fixed_image.shape != moving_image.shape:
        fixed_image, moving_image = zero_pad_arrays(fixed_image, moving_image)
        logger.debug(f'Padded moving image shape: {moving_image.shape}')
        logger.debug(f'Padded fixed image shape: {fixed_image.shape}')

    crop_width_x, crop_width_y, overlap_x, overlap_y = get_cropping_params(fixed_image)

    fixed_crop, moving_crop = get_dense_crop(moving_image, fixed_image, crop_width_x, crop_width_y, overlap_x, overlap_y)
    
    logger.info(f'Computing affine transformation matrix.')
    matrix = compute_affine_mapping_cv2(fixed_crop[:,:,2], moving_crop[:,:,2], crop, crop_size, n_features)
    logger.info(f'Transformation computed successfully.')
    
    del fixed_image, fixed_crop, moving_crop
    gc.collect()
    
    crops = crop_2d_array_grid(image=moving_image, crop_width_x=crop_width_x, crop_width_y=crop_width_y, overlap_x=overlap_x, overlap_y=overlap_y)
    
    del moving_image
    gc.collect()
    
    logger.info(f'Applying transformation to moving crops.')
    mapped_crops = apply_mappings(matrix, crops, 'cv2')
    logger.info(f'Transformations applied successfully.')

    del crops
    gc.collect()
    
    logger.info(f'Exporting registered image to {output_path}.')
    export_image(registered_crops=mapped_crops, overlap_x=overlap_x, overlap_y=overlap_y, output_path=output_path)
    logger.info(f'Image exported successfully to {output_path}.')
    
    del mapped_crops
    gc.collect()

def main(args):
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    affine_registration(args.input_path, args.output_path, args.fixed_image_path, args.crop, args.crop_size, args.n_features)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to input images.')
    parser.add_argument('--output-path', type=str, required=True, 
                        help='Path to registered image.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to fixed image')
    parser.add_argument('--crop', action='store_false', 
                        help='Use a smaller region to compute the affine mapping.')
    parser.add_argument('--crop-size', type=int, default=4000,
                        help='Size of the subregion used for affine mapping (if `crop` is True).')
    parser.add_argument('--n-features', type=int, default=2000,
                        help='Number of features to be found for affine mapping.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to directory where log files will be stored.')
    args = parser.parse_args()
    main(args)