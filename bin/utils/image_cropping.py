#!/usr/bin/env python

import os
import gc
import logging
import tifffile
import nd2
import h5py
import numpy as np
from .io import load_pickle, save_pickle, load_h5
from . import logging_config 

logging_config.setup_logging()
logger = logging.getLogger(__name__)


"""
Image cropping
"""

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
        # Extract the start and end rows/columns from the cropping area.
        start_row, end_row, start_col, end_col = area
        # Return the cropped portion of the array.
        return array[start_row:end_row, start_col:end_col]

    # If a single crop area is provided, crop and return that area directly.
    if len([crop_areas]) == 1:
        return crop_area(crop_areas)
    
    # If no crop indices are provided, return a list of cropped areas.
    if crop_indices is None:
        return [crop_area(area) for area in crop_areas]
    else:
        # Return a list of tuples containing indices and corresponding cropped areas.
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
    # Validate crop width against overlap value.
    if crop_width <= overlap:
        raise ValueError("Crop width must be greater than overlap.")

    # Ensure that either 'image' or 'shape' is provided, but not both.
    if (shape is None and image is None) or (shape is not None and image is not None):
        raise TypeError("You must provide either 'image' or 'shape', but not both.")

    # If 'image' is provided, use its shape; otherwise, use the provided shape.
    if image is not None: 
        shape = image.shape
    
    # Determine the dimension to calculate positions based on the specified axis.
    dim = shape[1] if axis == 0 else shape[0]

    stride = int(crop_width - overlap)  # Calculate stride based on crop width and overlap.
    start_positions = np.arange(0, dim - stride, stride)  # Generate starting positions for crops.
    n_crops = len(start_positions)  # Count the number of crops.
    end_positions = start_positions[0:n_crops] + crop_width  # Calculate ending positions for each crop.

    # Adjust start and end positions if the last crop exceeds the dimension.
    if end_positions[n_crops - 1] < dim:
        start_positions = np.append(start_positions, end_positions[n_crops - 1] - overlap)
        end_positions = np.append(end_positions, dim)
    elif end_positions[n_crops - 1] > dim:
        end_positions[n_crops - 1] = end_positions[n_crops - 1] - (end_positions[n_crops - 1] - dim)

    # Create an array of start and end positions to return.
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
    crop_areas = []  # Initialize a list to hold crop areas.
    crop_indices = []  # Initialize a list to hold crop indices.

    # If both positions are tuples, return the area directly as a single tuple.
    if isinstance(horizontal_positions, tuple) and isinstance(vertical_positions, tuple):
        crop_area = (horizontal_positions[0], horizontal_positions[1], vertical_positions[0], vertical_positions[1])
        return crop_area

    # Iterate over vertical positions and horizontal positions to create crop areas.
    for v_pos_idx in range(vertical_positions.shape[1]):
        for h_pos_idx in range(horizontal_positions.shape[1]):
            v_pos = vertical_positions[:, v_pos_idx]
            h_pos = horizontal_positions[:, h_pos_idx]
            crop_index = (h_pos_idx, v_pos_idx)

            crop_indices.append(crop_index)  # Append the crop index.
            crop_areas.append((h_pos[0], h_pos[1], v_pos[0], v_pos[1]))  # Append the crop area.

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
    # Calculate vertical cropping positions based on provided parameters.
    vertical_positions = get_cropping_positions(image=image, shape=shape, overlap=overlap_x, crop_width=crop_width_x, axis=0)
    # Calculate horizontal cropping positions based on provided parameters.
    horizontal_positions = get_cropping_positions(image=image, shape=shape, overlap=overlap_y, crop_width=crop_width_y, axis=1)
    # Create crop indices and areas using the horizontal and vertical positions.
    crop_indices, crop_areas = make_crop_areas_list(horizontal_positions, vertical_positions)

    # Return crop indices and areas if requested, otherwise return only areas.
    if get_indices:
        return crop_indices, crop_areas
    else:
        return crop_areas

def load_tiff_region(path, loading_region):
    """
    Load a specified region from a TIFF file.

    Parameters:
        path (str): The path to the TIFF file.
        loading_region (tuple): A tuple defining the region to load (start_row, end_row, start_col, end_col).

    Returns:
        np.ndarray: A multi-channel image array loaded from the specified region.
    """
    # Open the TIFF file
    with tifffile.TiffFile(path) as tif:
        # Unpack the coordinates from loading_region
        start_row, end_row, start_col, end_col = loading_region
        
        # Define the region to load (slices for rows and columns)
        region = (slice(start_row, end_row), slice(start_col, end_col))
        
        # Load the specified region from each page (channel) and stack them
        loaded_region = []  # List to hold loaded channels
        
        for page in tif.pages:
            # Read the region from each page (channel)
            channel_region = page.asarray()[region[0], region[1]]
            loaded_region.append(channel_region)  # Append the loaded channel region
        
        # Stack the loaded regions along a new axis to form a multi-channel image
        multi_channel_image = np.stack(loaded_region, axis=-1)
    
    return multi_channel_image

def load_h5_region(file_path, loading_region):
    """
    Read a specific region from an HDF5 file.
    
    Parameters:
    -----------
    file_path : str
        Path to the HDF5 file
    dataset_name : str
        Name of the dataset in the HDF5 file
    x_start, x_end : int
        Start and end coordinates for x (columns)
    y_start, y_end : int
        Start and end coordinates for y (rows)
    """

    start_row, end_row, start_col, end_col = loading_region
    with h5py.File(file_path, 'r') as f:
        return f['dataset'][start_col:end_col, start_row:end_row]

def get_image_file_shape(path, format='.h5'):
    """
    Get the width and height of a TIFF image without fully loading the image.
    
    Parameters:
        tiff_path (str): Path to the TIFF image.
    
    Returns:
        tuple: (width, height) of the image.
    """

    if format == 'tiff' or format == '.tiff':
        with tifffile.TiffFile(path) as tiff:
            image_shape = tiff.pages[0].shape  # (height, width)
            width, height = image_shape[1], image_shape[0]  # Extract width and height
    
    if format == 'nd2' or format == '.nd2':
        with nd2.ND2File(path) as nd2_file:
                # Get the dimensions of the first image
                first_image_shape = nd2_file.asarray()[0].shape  # (channels, height, width) format
                
                # Assuming the first image is the one we want, extract height and width
                width, height = first_image_shape[2], first_image_shape[1] # (channels, height, width)

    if format == '.h5' or format == 'h5':
        with h5py.File(path, 'r') as f:
            shape = f['dataset'].shape
            width, height = shape[0], shape[1]
        
    return width, height

def get_padding_shape(shape1, shape2):
    """
    Calculate the target shape for padding by determining the maximum dimensions.

    Parameters:
        shape1 (tuple): Shape of the first array.
        shape2 (tuple): Shape of the second array.

    Returns:
        tuple: The target shape that both arrays should conform to.
    """
    # Determine the target shape by taking the maximum of each dimension
    target_shape = tuple(max(shape1[i], shape2[i]) for i in range(len(shape1)))

    return target_shape

def zero_pad_array(array, target_shape):
    """
    Pad a NumPy array with zeros to match a specified target shape.

    Parameters:
        array (np.ndarray): The input array to be padded.
        target_shape (tuple): The target shape for the array.

    Returns:
        np.ndarray: The zero-padded array.
    """
    arr_shape = array.shape

    print(f"ARRAY SHAPE: {arr_shape}")
    print(f"TARGET SHAPE: {target_shape}")

    # Only pad if necessary
    if arr_shape != target_shape:
        # Calculate the padding width for each dimension
        pad_width = [(0, target_shape[i] - arr_shape[i]) for i in range(len(arr_shape))]
        print(f"PAD WIDTH: {pad_width}")
        # Apply zero padding
        array = np.pad(array, pad_width, mode='constant')
    
    return array

def crop_image_channels(input_path, fixed_image_path, current_crops_dir, crop_width_x, crop_width_y, overlap_x, overlap_y, which_crop='fixed'):
    """
    Crops both the moving and fixed images and saves the crops to directories.
    
    Args:
        input_path (str): Path to the moving image.
        fixed_image_path (str): Path to the fixed image.
        current_crops_dir (str): Directory where the image crops will be saved.
        crop_width_x (int): Width of each crop.
        crop_width_y (int): Height of each crop.
        overlap_x (int): Overlap between crops along the x-axis.
        overlap_y (int): Overlap between crops along the y-axis.
        which_crop (str): Which image to crop. Either 'fixed' or 'moving'.
        
    Returns:
        tuple: Directories for fixed image crops and moving image crops. The saved arrays have shape (height, width, n_channels).
    """
    # Define image to be loaded
    if which_crop == 'fixed':
        path_to_load = fixed_image_path
        whole_slide_id = os.path.basename(fixed_image_path).split('.')[0]
    if which_crop == 'moving':
        path_to_load = input_path
        whole_slide_id = os.path.basename(input_path).split('.')[0]

    # Get image shapes and compute padding
    mov_shape = get_image_file_shape(input_path)  # Shape of moving image
    fixed_shape = get_image_file_shape(fixed_image_path)  # Shape of fixed image
    padding_shape = get_padding_shape(mov_shape, fixed_shape)  # Calculate padding shape

    # Compute crop areas
    crop_areas = get_crop_areas(shape=padding_shape, crop_width_x=crop_width_x, crop_width_y=crop_width_y, overlap_x=overlap_x, overlap_y=overlap_y)
    
    os.makedirs(current_crops_dir, exist_ok=True)

    # Loop through each channel and apply padding
    n_channels = 3  # Number of channels in the image
    for ch in range(n_channels):
        # Read the fixed image and select the current channel
        for index, area in zip(crop_areas[0], crop_areas[1]):
            crop_save_path = os.path.join(current_crops_dir, f'{whole_slide_id}_{index[0]}_{index[1]}_{ch}.pkl')
            if not os.path.exists(crop_save_path):
                logger.debug(f'Processing {whole_slide_id}_{index[0]}_{index[1]}_{ch}')

                logger.debug(f"Loading image {path_to_load}")
                image = load_h5(path_to_load, channels_to_load=[ch])
                
                # Crop the image using the specified crop area
                crop = (
                    index + (ch,), 
                    crop_2d_array(zero_pad_array(np.squeeze(image), padding_shape), crop_areas=area)
                )

                # Save each crop individually with a unique name
                save_pickle(crop, crop_save_path)  # Save the crop using pickle               
                logger.debug(f'Saved crop ({index[0]}, {index[1]}, {ch}) to {crop_save_path}')

                del crop, image
                gc.collect()

"""
Overlap removal
"""

import itertools
from concurrent.futures import ProcessPoolExecutor

def remove_overlap(crop, indices: list, overlap: int, axis: int = 0):
    """
    Remove overlapping regions from adjacent crops along a specified axis.

    Args:
        crops (list): List of tuples where each tuple contains an index and a 2D numpy array.
                      The index tuple consists of (row, column, image channel).
        overlap (int): Size of overlap between adjacent crops.
        axis (int): Axis along which to remove the overlap:
                    - 0 for rows
                    - 1 for columns

    Returns:
        list: List of tuples containing the adjusted crops without overlaps.
    """
    overlap_half_left = overlap // 2
    overlap_half_right = overlap - overlap_half_left

    idx, crop = crop[0], crop[1]

    max_rows = max(idx[0] for idx in indices)
    max_cols = max(idx[1] for idx in indices)

    # Sort crops by row and then by column
    indices = sorted(indices, key=lambda x: (x[0], x[1]))

    start_row, end_row, start_col, end_col = 0, crop.shape[0], 0, crop.shape[1]

    # Handle row overlap
    if axis == 0:
        if idx[0] != 0:  # If not the first crop in the row
            start_row += overlap_half_left
        if idx[0] != max_rows:  # If not the last crop in the row
            end_row -= overlap_half_right

    # Handle column overlap
    elif axis == 1:
        if idx[1] != 0:  # If not the first crop in the column
            start_col += overlap_half_left
        if idx[1] != max_cols:  # If not the last crop in the column
            end_col -= overlap_half_right

    # Extract the crop area without overlap
    crop = crop[start_row:end_row, start_col:end_col]
    
    return (idx, crop)

def get_stitching_positions(shapes: list):
    """
    Calculate the positions where each cropped image will be placed in the final stitched image.

    Args:
        crops (list): List of tuples where each tuple contains an index and a 2D numpy array 
                      representing the cropped image. The index tuple consists of (row, column, image channel).

    Returns:
        list: A list of (row, col) positions where each crop will be placed in the final stitched image.
    """
    # Determine the number of crop rows and columns
    n_crop_rows = np.max([element[0][0] for element in shapes]) + 2
    n_crop_cols = np.max([element[0][1] for element in shapes]) + 2

    # Calculate row stitching positions
    sorted_shapes = sorted(shapes, key=lambda x: x[0][1])
    if n_crop_rows - 1 > 1:
        crops_rows = [shape[0] for idx, shape in sorted_shapes][:n_crop_rows - 2]
    else:
        crops_rows = [shape[0] for idx, shape in sorted_shapes][:n_crop_rows - 1]

    crops_rows = np.insert(crops_rows, 0, 0)
    stitching_positions_h = np.cumsum(crops_rows)

    # Calculate column stitching positions
    sorted_shapes = sorted(shapes, key=lambda x: x[0][0])
    if n_crop_cols - 1 > 1:
        crops_cols = [shape[1] for idx, shape in sorted_shapes][:n_crop_cols - 2]
    else:
        crops_cols = [shape[1] for idx, shape in sorted_shapes][:n_crop_cols - 1]

    crops_cols = np.insert(crops_cols, 0, 0)
    stitching_positions_v = np.cumsum(crops_cols)

    # Generate stitching positions
    stitching_positions = list(itertools.product(stitching_positions_h, stitching_positions_v))

    return stitching_positions

def process_crop(path, indices, overlap_x, overlap_y, checkpoint_dir):
    crop = load_pickle(path)
    # Assuming 'indices' are defined or passed as arguments if necessary
    crop = remove_overlap(crop, indices, overlap_x, 0)
    crop = remove_overlap(crop, indices, overlap_y, 1)
    crop_id = os.path.basename(path).split('.')[0]
    checkpoint_path = os.path.join(checkpoint_dir, f'{crop_id}.pkl')

    shape_info = (crop[0], crop[1].shape)

    if not os.path.exists(checkpoint_path):
        save_pickle(crop, checkpoint_path)
        
    return shape_info

def remove_crops_overlap(crops_paths, checkpoint_dir, overlap_x, overlap_y, max_workers):
    n_channels = 3
    
    # List to store the resulting shapes for stitching
    shapes = []
    
    # Create a ProcessPoolExecutor to parallelize crop processing
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for ch in range(n_channels):
            indices = [path[0] for path in crops_paths if path[0][2] == ch]
            paths = [path[1] for path in crops_paths if path[0][2] == ch]
            for path in paths:
                # Submit the crop processing to the pool
                futures.append(executor.submit(process_crop, path, indices, overlap_x, overlap_y, checkpoint_dir))
        
        # Collect the results as they complete
        for future in futures:
            shapes.append(future.result())
    
    positions = get_stitching_positions(shapes)
    return positions