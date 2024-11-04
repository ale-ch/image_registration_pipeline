#!/usr/bin/env python

import numpy as np
import gc
import argparse
import logging
import os
from utils import logging_config
from utils.misc import create_checkpoint_dirs
from utils.image_cropping import load_h5_region
from utils.image_cropping import get_image_file_shape
from utils.image_cropping import get_padding_shape
from utils.image_cropping import zero_pad_array
from utils.image_cropping import crop_2d_array
from utils.image_cropping import get_crop_areas
from utils.image_mapping import compute_affine_mapping_cv2
from utils.wrappers.apply_mappings import apply_mapping
from utils.io_tools import save_pickle, load_nd2, load_h5


logging_config.setup_logging()
logger = logging.getLogger(__name__)

def binarize_image(image, thresh=None, alpha=1.5):
    if thresh == None:
        thresh = np.mean(image)
    return (image > thresh * alpha).astype('int8')

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

def get_dense_crop(input_path, fixed_image_path, crop_areas, nonzero_thresh=0.15):
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
        moving_crop = load_h5_region(input_path, area)
        fixed_crop = load_h5_region(fixed_image_path, area)

        # Select DAPI channel (channel 2)
        moving_crop = np.squeeze(moving_crop[:, :, 2])
        fixed_crop = np.squeeze(fixed_crop[:, :, 2])

        # Pad the crops if needed
        moving_shape = moving_crop.shape
        fixed_shape = fixed_crop.shape
        padding_shape = get_padding_shape(moving_shape, fixed_shape)
        moving_crop = zero_pad_array(moving_crop, padding_shape)
        fixed_crop = zero_pad_array(fixed_crop, padding_shape)
        nonzero_prop = np.mean(binarize_image(moving_crop))
        
        # Stop cropping if sufficient non-zero pixels are found
        if nonzero_prop >= nonzero_thresh:
            break

    return fixed_crop, moving_crop

def affine_registration(input_path, fixed_image_path, current_registered_crops_dir, 
                        crop_width_x, crop_width_y, overlap_x, overlap_y, crop=False, crop_size=4000, n_features=2000):
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
    # Get image shape and determine crop areas
    mov_shape = get_image_file_shape(input_path)
    fixed_shape = get_image_file_shape(fixed_image_path)
    padding_shape = get_padding_shape(mov_shape, fixed_shape)
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
    moving_image = load_h5(input_path)
    # Apply the affine transformation to each crop and channel
    n_channels = 3
    for ch in range(n_channels):
        for idx, area in zip(crop_areas[0], crop_areas[1]):
            checkpoint_filename = os.path.join(current_registered_crops_dir, f'affine_split_{idx[0]}_{idx[1]}_{ch}.pkl')
            if not os.path.exists(checkpoint_filename):
                crop = crop_2d_array(
                    array=zero_pad_array(
                        array=np.squeeze(moving_image[:, :, ch]), 
                        target_shape=padding_shape
                    ),
                    crop_areas=area
                )

                logger.info(f'Applying transformation to moving crops.')
                crop = ((idx) + (ch,), apply_mapping(matrix, crop, 'cv2'))
                logger.info(f'Transformation applied successfully.')

                # Save the transformed crop
                save_pickle(crop, checkpoint_filename)

    del moving_image, crop
    gc.collect()


def main(args):
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    input_path = args.input_path.replace('.nd2', '.h5')
    fixed_image_path = args.fixed_image_path.replace('.nd2', '.h5')

    filename = os.path.basename(input_path) # Name of the output file 
    dirname = os.path.basename(os.path.dirname(input_path)) # Name of the parent directory to output file
    file_output_dir = os.path.join(args.output_dir, 'affine', dirname) # Path to parent directory of the output file
    output_path = os.path.join(file_output_dir, filename) # Path to output output file

    # Get image shape and determine crop areas
    mov_shape = get_image_file_shape(input_path)
    fixed_shape = get_image_file_shape(fixed_image_path)
    padding_shape = get_padding_shape(mov_shape, fixed_shape)
    crop_areas = get_crop_areas(
        shape=padding_shape, 
        crop_width_x=args.crop_width_x, crop_width_y=args.crop_width_y, 
        overlap_x=args.overlap_x, overlap_y=args.overlap_y
    )

    # Get checkpoint directories
    _, current_registered_crops_dir, _ = create_checkpoint_dirs(
        root_registered_crops_dir=args.registered_crops_dir, 
        moving_image_path=input_path,
        transformation='affine',
        makedirs=False
    )

    n_registered_crops = len(os.listdir(current_registered_crops_dir))
    n_crops = len(crop_areas[0])
    
    if not os.path.exists(output_path) or n_registered_crops != n_crops:
        # Get checkpoint directories
        _, current_registered_crops_dir, _ = create_checkpoint_dirs(
            root_registered_crops_dir=args.registered_crops_dir, 
            moving_image_path=input_path,
            transformation='affine'
        )

        # Perform affine registration
        affine_registration(input_path, fixed_image_path, current_registered_crops_dir, 
                            args.crop_width_x, args.crop_width_y, args.overlap_x, args.overlap_y,
                            args.crop, args.crop_size, args.n_features)
        

if __name__ == '__main__':
    # Set up argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to the input (moving) image.')
    parser.add_argument('--output-dir', type=str, required=True, 
                        help='Path to save the registered image.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to the fixed image used for registration.')
    parser.add_argument('--registered-crops-dir', type=str, required=True, 
                        help='Directory to save intermediate registered crops.')
    parser.add_argument('--crop-width-x', required=True, type=int, 
                        help='Width of each crop.')
    parser.add_argument('--crop-width-y', required=True, type=int, 
                        help='Height of each crop.')
    parser.add_argument('--overlap-x', type=int, 
                        help='Overlap of each crop along the x-axis.')
    parser.add_argument('--overlap-y', type=int, 
                        help='Overlap of each crop along the y-axis.')
    parser.add_argument('--crop', action='store_true', 
                        help='Whether to compute the affine mapping using a smaller subregion of the image.')
    parser.add_argument('--crop-size', type=int, default=4000, 
                        help='Size of the subregion to use for affine mapping (if cropping is enabled).')
    parser.add_argument('--n-features', type=int, default=2000, 
                        help='Number of features to detect for computing the affine transformation.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Directory to store log files.')
    parser.add_argument('--delete-checkpoints', action='store_false', 
                        help='Delete intermediate files after processing.')
    args = parser.parse_args()
    main(args)
