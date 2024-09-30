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
    """
    Determines cropping parameters based on the size of the input image.
    
    Args:
        shape (tuple): Shape of the padded image.
    
    Returns:
        tuple: Crop width and overlap for both x and y dimensions.
    """
    # Check if the image size exceeds the limitations of cv2.warpAffine and adjust crop fractions
    if shape[0] > 64000:
        crop_fraction_y = 3
    else:
        crop_fraction_y = 2
    
    if shape[1] > 64000:
        crop_fraction_x = 3
    else:
        crop_fraction_x = 2
    
    # Define crop dimensions and overlap
    crop_width_y = shape[0] // crop_fraction_y
    crop_width_x = shape[1] // crop_fraction_x
    overlap_y = int(crop_width_y // 1.5)
    overlap_x = int(crop_width_x // 1.5)

    return crop_width_x, crop_width_y, overlap_x, overlap_y

def get_dense_crop(input_path, fixed_image_path, crop_areas):
    """
    Loads and pads image crops, ensuring minimal zero-valued pixels in the moving image.
    
    Args:
        input_path (str): Path to the moving image.
        fixed_image_path (str): Path to the fixed image.
        crop_areas (list): List of areas to crop from the input images.
    
    Returns:
        tuple: Fixed crop and moving crop arrays after padding.
    """
    for area in crop_areas:
        # Load specific region of the images for comparison
        moving_crop = load_tiff_region(input_path, area)
        fixed_crop = load_tiff_region(fixed_image_path, area)

        # Select DAPI channel (channel 2)
        moving_crop = np.squeeze(moving_crop[:, :, 2])
        fixed_crop = np.squeeze(fixed_crop[:, :, 2])

        # Pad the crops if needed
        moving_shape = moving_crop.shape
        fixed_shape = fixed_crop.shape
        padding_shape = get_padding_shape(moving_shape, fixed_shape)
        moving_crop = zero_pad_array(moving_crop, padding_shape)
        fixed_crop = zero_pad_array(fixed_crop, padding_shape)

        # Check the proportion of zero-valued pixels in the moving crop
        moving_crop_scaled = (moving_crop - np.min(moving_crop))
        zero_prop = (moving_crop_scaled.size - np.count_nonzero(moving_crop_scaled)) / moving_crop_scaled.size

        del moving_crop_scaled
        gc.collect()

        # Stop cropping if sufficient non-zero pixels are found
        if zero_prop <= 0.3:
            break

    return fixed_crop, moving_crop

def affine_registration(input_path, output_path, fixed_image_path, current_registered_crops_dir, crop=True, crop_size=4000, n_features=2000):
    """
    Registers moving and fixed images using an affine transformation and saves the registered image.

    Args:
        input_path (str): Path to the moving image.
        output_path (str): Path to save the registered image.
        fixed_image_path (str): Path to the fixed image used for registration.
        current_registered_crops_dir (str): Directory to store intermediate crops.
        crop (bool): Whether to compute affine mapping using a smaller region.
        crop_size (int): Size of the subregion for affine mapping.
        n_features (int): Number of features to use for the affine transformation.
    """
    logger.info(f'Output path: {output_path}')

    # Ensure output directory exists
    output_dir_path = os.path.dirname(output_path)
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
        logger.debug(f'Output directory created successfully: {output_dir_path}')

    # Get image shape and determine crop areas
    mov_shape = get_tiff_image_shape(input_path)
    fixed_shape = get_tiff_image_shape(fixed_image_path)
    padding_shape = get_padding_shape(mov_shape, fixed_shape)
    crop_width_x, crop_width_y, overlap_x, overlap_y = get_cropping_params(padding_shape)
    crop_areas = get_crop_areas(shape=padding_shape, crop_width_x=crop_width_x, crop_width_y=crop_width_y, overlap_x=overlap_x, overlap_y=overlap_y)

    # Find a dense region to compute the affine transformation matrix
    fixed_crop, moving_crop = get_dense_crop(input_path, fixed_image_path, crop_areas[1])

    logger.info(f'Computing affine transformation matrix.')
    matrix = compute_affine_mapping_cv2(fixed_crop, moving_crop, crop, crop_size, n_features)
    logger.info(f'Transformation computed successfully.')

    del moving_crop
    gc.collect()

    # Load and pad the moving image
    logger.debug(f"Loading moving image {input_path}")
    moving_image = imread(input_path)

    # Apply the affine transformation to each crop and channel
    n_channels = 3
    for ch in range(n_channels):
        for idx, area in zip(crop_areas[0], crop_areas[1]):
            checkpoint_filename = os.path.join(current_registered_crops_dir, f'affine_split_{idx[0]}_{idx[1]}_{ch}.pkl')
            if not os.path.exists(checkpoint_filename):
                crop = crop_2d_array(
                    array=zero_pad_array(np.squeeze(moving_image[:, :, ch]), padding_shape),
                    crop_areas=area
                )

                logger.info(f'Applying transformation to moving crops.')
                crop = ((idx) + (ch,), apply_mapping(matrix, crop, 'cv2'))
                logger.info(f'Transformation applied successfully.')

                # Save the transformed crop
                save_pickle(crop, checkpoint_filename)

    del moving_image, crop
    gc.collect()

    # Gather all registered crops and export the final registered image
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

    # Create checkpoint directories
    _, current_registered_crops_dir, _ = create_checkpoint_dirs(
        root_registered_crops_dir=args.registered_crops_dir, 
        moving_image_path=args.input_path
    )
    
    # Perform affine registration
    affine_registration(args.input_path, args.output_path, args.fixed_image_path, current_registered_crops_dir, args.crop, args.crop_size, args.n_features)

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
    parser.add_argument('--crop', action='store_false', 
                        help='Whether to compute the affine mapping using a smaller subregion of the image.')
    parser.add_argument('--crop-size', type=int, default=4000, 
                        help='Size of the subregion to use for affine mapping (if cropping is enabled).')
    parser.add_argument('--n-features', type=int, default=2000, 
                        help='Number of features to detect for computing the affine transformation.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Directory to store log files.')
    args = parser.parse_args()
    main(args)
