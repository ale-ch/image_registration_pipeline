#!/usr/bin/env python

import numpy as np
import gc
import argparse
import logging
import os
from utils import logging_config
from skimage.io import imread
from utils.wrappers.create_checkpoint_dirs import create_checkpoint_dirs
from utils.image_cropping import load_tiff_region
from utils.image_cropping import get_tiff_image_shape
from utils.image_cropping import get_padding_shape
from utils.image_cropping import zero_pad_array
from utils.image_cropping import crop_2d_array
from utils.image_cropping import get_crop_areas
from utils.image_mapping import compute_affine_mapping_cv2
from utils.wrappers.apply_mappings import apply_mapping
from utils.pickle_utils import save_pickle, load_pickle
from utils.wrappers.export_image import export_image

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def get_cropping_params(shape):    
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

def get_dense_crop(input_path, fixed_image_path, crop_areas):    
    for area in crop_areas:
        moving_crop = load_tiff_region(input_path, area)
        fixed_crop = load_tiff_region(fixed_image_path, area)

        moving_crop = np.squeeze(moving_crop[:,:,2])
        fixed_crop = np.squeeze(fixed_crop[:,:,2])

        moving_shape = moving_crop.shape
        fixed_shape = fixed_crop.shape
        padding_shape = get_padding_shape(moving_shape, fixed_shape)

        moving_crop = zero_pad_array(moving_crop, padding_shape)
        fixed_crop = zero_pad_array(fixed_crop, padding_shape)
    
        # Compute percentage of zero-valued pixels in image
        moving_crop_scaled = (moving_crop - np.min(moving_crop))
        zero_prop = (moving_crop_scaled.size - np.count_nonzero(moving_crop_scaled)) / moving_crop_scaled.size
    
        del moving_crop_scaled
        gc.collect()
    
        if zero_prop <= 0.3:
            break

    return fixed_crop, moving_crop

def affine_registration(input_path, output_path, fixed_image_path, current_registered_crops_dir, crop=True, crop_size=4000, n_features=2000):
    logger.info(f'Output path: {output_path}')

    # Check if output image directory exists 
    output_dir_path = os.path.dirname(output_path)
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
        logger.debug(f'Output directory created successfully: {output_dir_path}')

    # Compute cropping areas 
    mov_shape = get_tiff_image_shape(input_path)
    fixed_shape = get_tiff_image_shape(fixed_image_path)
    padding_shape = get_padding_shape(mov_shape, fixed_shape)
    crop_width_x, crop_width_y, overlap_x, overlap_y = get_cropping_params(padding_shape)
    crop_areas = get_crop_areas(shape=padding_shape, crop_width_x=crop_width_x, crop_width_y=crop_width_y, overlap_x=overlap_x, overlap_y=overlap_y)

    # Find first dense crop to compute affine transformation
    fixed_crop, moving_crop = get_dense_crop(input_path, fixed_image_path, crop_areas[1])
    
    logger.info(f'Computing affine transformation matrix.')
    matrix = compute_affine_mapping_cv2(fixed_crop, moving_crop, crop, crop_size, n_features)
    logger.info(f'Transformation computed successfully.')
    
    del moving_crop
    gc.collect()

    # Load moving image and pad to size
    logger.debug(f"Loading moving image {input_path}")
    moving_image  = imread(input_path)
    # logger.debug(f'Padded moving image shape: {moving_image.shape}')

    # Apply mapping to each individual crop, by channel
    n_channels = 3
    for ch in range(n_channels):
        for idx, area in zip(crop_areas[0], crop_areas[1]):
            checkpoint_filename = os.path.join(current_registered_crops_dir, f'affine_split_{idx[0]}_{idx[1]}_{ch}.pkl')
            if not os.path.exists(checkpoint_filename):
                crop = crop_2d_array(
                    array=zero_pad_array(np.squeeze(moving_image[:,:,ch]), padding_shape), 
                    crop_areas=area
                )

                logger.info(f'Applying transformation to moving crops.')
                crop = ((idx) + (ch,), apply_mapping(matrix, crop, 'cv2'))
                logger.info(f'Transformation applied successfully.')
                
                # Save mapped crop
                save_pickle(crop, checkpoint_filename)    
    
    del moving_image, crop
    gc.collect() 

    registered_crops = []
    checkpoint_files = os.listdir(current_registered_crops_dir) 
    checkpoint_files = [os.path.join(current_registered_crops_dir, file) for file in checkpoint_files]
    for file in checkpoint_files:
        registered_crop = load_pickle(file)
        registered_crops.append(registered_crop)
    
    logger.info(f'Exporting registered image to {output_path}.')
    export_image(registered_crops=registered_crops, overlap_x=overlap_x, overlap_y=overlap_y, output_path=output_path)
    logger.info(f'Image exported successfully to {output_path}.')
    
    del registered_crops
    gc.collect()

def main(args):
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    _, current_registered_crops_dir, _ = create_checkpoint_dirs(root_registered_crops_dir=args.registered_crops_dir, 
                                                                moving_image_path=args.input_path)
    affine_registration(args.input_path, args.output_path, args.fixed_image_path, current_registered_crops_dir, args.crop, args.crop_size, args.n_features)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to input images.')
    parser.add_argument('--output-path', type=str, required=True, 
                        help='Path to registered image.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to fixed image.')
    parser.add_argument('--registered-crops-dir', type=str, required=True, 
                        help='Root directory to save registered crops.')
    parser.add_argument('--crop', action='store_false', 
                        help='Use a smaller region to compute the affine mapping.')
    parser.add_argument('--crop-size', type=int, default=2000, # 4000
                        help='Size of the subregion used for affine mapping (if `crop` is True).')
    parser.add_argument('--n-features', type=int, default=500, # 2000
                        help='Number of features to be found for affine mapping.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to directory where log files will be stored.')
    args = parser.parse_args()
    main(args)