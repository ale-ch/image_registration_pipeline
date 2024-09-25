#!/usr/bin/env python

import os
import re
import gc
import logging
import tifffile
import numpy as np
from skimage.io import imread
from utils.pickle_utils import save_pickle
from utils import logging_config 

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def crop_2d_array(array, crop_areas, crop_indices=None):
    """
    Crop a 2D NumPy array into specified areas.

    Parameters:
        array (np.ndarray): The input 2D array.
        crop_areas (tuple or list): A tuple or a list of tuples of four integers (start_row, end_row, start_col, end_col).
        crop_indices (list, optional): A list of indices corresponding to the crop areas.

    Returns:
        np.ndarray or list: The cropped 2D array or a list of cropped arrays (optionally with indices).
    """
    def crop_area(area):
        start_row, end_row, start_col, end_col = area
        return array[start_row:end_row, start_col:end_col]

    if len([crop_areas]) == 1:
        return crop_area(crop_areas)
    if crop_indices is None:
        return [crop_area(area) for area in crop_areas]
    else:
        return [(idx, crop_area(area)) for idx, area in zip(crop_indices, crop_areas)]


def get_cropping_positions(crop_width: int, overlap: int, axis=0, image=None, shape=None):
    """
    Calculate the cropping positions for an image along a specified axis.

    Parameters:
        image (np.ndarray): The input 2D array representing the image to be cropped. Shape is (n_rows, n_cols, ...).
        shape (tuple): shape of the image to be cropped. Must be (n_rows, n_cols, ...).
        crop_width (int): The width of each crop.
        overlap (int): The number of columns that each crop should overlap with the previous one.
        axis (int, optional): The axis along which to calculate the positions. 0 for columns, 1 for rows. Defaults to 0.

    Returns:
        np.ndarray: A 2D array where the first row contains the starting indices and the second row contains the ending indices for each crop.
    """
    if crop_width <= overlap:
        raise ValueError("Crop width must be greater than overlap.")

    if (shape is None and image is None) or (shape is not None and image is not None):
        raise TypeError("You must provide either 'image' or 'shape', but not both.")

    if image is not None: 
        shape = image.shape
    
    dim = shape[1] if axis == 0 else shape[0]

    stride = int(crop_width - overlap)
    start_positions = np.arange(0, dim - stride, stride)
    n_crops = len(start_positions)
    end_positions = start_positions[0:n_crops] + crop_width

    if end_positions[n_crops - 1] < dim:
        start_positions = np.append(start_positions, end_positions[n_crops - 1] - overlap)
        end_positions = np.append(end_positions, dim)
    elif end_positions[n_crops - 1] > dim:
        end_positions[n_crops - 1] = end_positions[n_crops - 1] - (end_positions[n_crops - 1] - dim)

    positions = np.array([start_positions, end_positions])

    return positions

def make_crop_areas_list(horizontal_positions, vertical_positions):
    """
    Generate a list of crop areas based on horizontal and vertical positions.

    Parameters:
        horizontal_positions (np.ndarray): Array of horizontal cropping positions.
        vertical_positions (np.ndarray): Array of vertical cropping positions.

    Returns:
        tuple: List of crop indices and list of crop areas.
    """
    crop_areas = []
    crop_indices = []

    if isinstance(horizontal_positions, tuple) and isinstance(vertical_positions, tuple):
        crop_area = (horizontal_positions[0], horizontal_positions[1], vertical_positions[0], vertical_positions[1])
        return crop_area

    for v_pos_idx in range(vertical_positions.shape[1]):
        for h_pos_idx in range(horizontal_positions.shape[1]):
            v_pos = vertical_positions[:, v_pos_idx]
            h_pos = horizontal_positions[:, h_pos_idx]
            crop_index = (h_pos_idx, v_pos_idx)

            crop_indices.append(crop_index)
            crop_areas.append((h_pos[0], h_pos[1], v_pos[0], v_pos[1]))

    return crop_indices, crop_areas

def get_crop_areas(crop_width_x: int, crop_width_y: int, overlap_x: int, overlap_y: int, image=None, shape=None, get_indices=True):
    """
    Calculate the crop areas for an image.

    Parameters:
        image (np.ndarray): The input image array.
        shape (tuple): Shape of image to be cropped. 
        crop_width_x (int): Width of each crop along the x-axis.
        crop_width_y (int): Width of each crop along the y-axis.
        overlap_x (int): Overlap along the x-axis.
        overlap_y (int): Overlap along the y-axis.
        get_indices (bool, optional): Whether to return crop indices. Defaults to True.

    Returns:
        tuple: Crop indices and crop areas, or only crop areas if get_indices is False.
    """
    vertical_positions = get_cropping_positions(image=image, shape=shape, overlap=overlap_x, crop_width=crop_width_x, axis=0)
    horizontal_positions = get_cropping_positions(image=image, shape=shape, overlap=overlap_y, crop_width=crop_width_y, axis=1)
    crop_indices, crop_areas = make_crop_areas_list(horizontal_positions, vertical_positions)

    if get_indices:
        return crop_indices, crop_areas
    else:
        return crop_areas

def load_tiff_region(path, loading_region):
    # Open the TIFF file
    with tifffile.TiffFile(path) as tif:
        # Unpack the coordinates from loading_region
        start_row, end_row, start_col, end_col = loading_region
        
        # Define the region to load (slices for rows and columns)
        region = (slice(start_row, end_row), slice(start_col, end_col))
        
        # Load the specified region from each page (channel) and stack them
        loaded_region = []
        
        for page in tif.pages:
            # Read the region from each page (channel)
            channel_region = page.asarray()[region[0], region[1]]
            loaded_region.append(channel_region)
        
        # Stack the loaded regions along a new axis to form a multi-channel image
        multi_channel_image = np.stack(loaded_region, axis=-1)
    
    return multi_channel_image

def get_tiff_image_shape(tiff_path):
    """
    Get the width and height of a TIFF image without fully loading the image.
    
    Parameters:
        tiff_path (str): Path to the TIFF image.
    
    Returns:
        tuple: (width, height) of the image.
    """
    with tifffile.TiffFile(tiff_path) as tiff:
        image_shape = tiff.pages[0].shape  # (height, width)
        width, height = image_shape[1], image_shape[0]
    return width, height

def get_padding_shape(shape1, shape2):
    # Determine the target shape by taking the maximum of each dimension
    target_shape = tuple(max(shape1[i], shape2[i]) for i in range(len(shape1)))

    return target_shape

def zero_pad_array(array, target_shape):
    arr_shape = array.shape
    # print(f"ARRAY SHAPE {arr_shape}")
    # Only pad if necessary
    if arr_shape != target_shape:
        pad_width = [(0, target_shape[i] - arr_shape[i]) for i in range(len(arr_shape))]
        array = np.pad(array, pad_width, mode='constant')
    
    return array

def save_image_crops(image, crop_areas, output_dir):
    """
    Loops through each crop area, processes the crop, and saves each crop individually.
    
    Args:
        image (ndarray): The input image (already padded if needed).
        crop_areas (tuple): Tuple containing crop indices and crop dimensions (from get_crop_areas).
        output_dir (str): Directory where crops will be saved.
    """
    # Check directory to save the crops
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.debug(f'Directory created: {output_dir}')
    
    # Loop through each crop and save it
    for index, area in zip(crop_areas[0], crop_areas[1]):
        logger.debug(f'Processing crop_{index[0]}_{index[1]}')
        
        # Crop the image
        crop = (index, crop_2d_array(image, crop_areas=area))
        
        # Save each crop individually with a unique name
        crop_save_path = os.path.join(output_dir, f'crop_{index[0]}_{index[1]}.pkl')
        save_pickle(crop, crop_save_path)
        
        logger.debug(f'Saved crop_{index[0]}_{index[1]} to {crop_save_path}')

def crop_images(input_path, fixed_image_path, current_crops_dir_fixed, current_crops_dir_moving, crop_width_x, crop_width_y, overlap_x, overlap_y):
    """
    Crops both the moving and fixed images and saves the crops to directories.
    
    Args:
        input_path (str): Path to the moving image.
        fixed_image_path (str): Path to the fixed image.
        crops_dir (str): Directory where crops will be saved.
        crop_width_x (int): Width of each crop.
        crop_width_y (int): Height of each crop.
        overlap_x (int): Overlap between crops along the x-axis.
        overlap_y (int): Overlap between crops along the y-axis.
        
    Returns:
        tuple: Directories for fixed image crops and moving image crops.
    """
    # Get image shapes and compute padding
    mov_shape = get_tiff_image_shape(input_path)
    fixed_shape = get_tiff_image_shape(fixed_image_path)
    padding_shape = get_padding_shape(mov_shape, fixed_shape)
    
    # Compute crop areas
    crop_areas = get_crop_areas(shape=padding_shape, crop_width_x=crop_width_x, crop_width_y=crop_width_y, overlap_x=overlap_x, overlap_y=overlap_y)

    # Fixed image: load, pad to size and crop
    logger.debug(f"Loading fixed image {fixed_image_path}")

    # Pre-allocate the array to hold the padded images
    n_channels = 3

    fixed_image_stacked = np.empty((padding_shape[0], padding_shape[1], n_channels))
    # Loop through each channel and apply padding
    for ch in range(n_channels):
        # Read the fixed image and select the current channel
        fixed_image = imread(fixed_image_path)[:, :, ch]
        
        # Pad the fixed image
        fixed_image = zero_pad_array(np.squeeze(fixed_image), padding_shape)
        
        # Store the padded image in the pre-allocated array
        fixed_image_stacked[:, :, ch] = fixed_image

    if not os.path.exists(current_crops_dir_fixed):
        save_image_crops(fixed_image_stacked, crop_areas, current_crops_dir_fixed)

    del fixed_image_stacked
    gc.collect()

    # Moving image: load, pad to size and crop
    logger.debug(f"Loading moving image {input_path}")

    # Pre-allocate the array to hold the padded images
    moving_image_stacked = np.empty((padding_shape[0], padding_shape[1], n_channels))
    # Loop through each channel and apply padding
    for ch in range(n_channels):
        # Read the fixed image and select the current channel
        image = imread(input_path)[:, :, ch]
        
        # Pad the fixed image
        image = zero_pad_array(np.squeeze(image), padding_shape)
        
        # Store the padded image in the pre-allocated array
        moving_image_stacked[:, :, ch] = image

    if not os.path.exists(current_crops_dir_moving):
        save_image_crops(moving_image_stacked, crop_areas, current_crops_dir_moving)

    del moving_image_stacked
    gc.collect()