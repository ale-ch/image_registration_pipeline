#!/usr/bin/env python

import numpy as np

from utils.image_mapping import compute_affine_mapping_cv2, apply_mapping

def compute_border_width(arr: np.ndarray, proportion=True):
    """
    Compute the width of borders of an image array that are filled with zeros.

    Parameters:
        arr (np.ndarray): Input 2D NumPy array.
        proportion (bool, optional): If True, returns the border widths as proportions of the array's dimensions. Defaults to True.

    Returns:
        tuple: Border widths as either proportions or absolute values (top, bottom, left, right).
    """    
    # Top border width
    top_width = 0
    for row in arr:
        if np.all(row == 0):
            top_width += 1
        else:
            break
    
    # Bottom border width
    bottom_width = 0
    for row in arr[::-1]:
        if np.all(row == 0):
            bottom_width += 1
        else:
            break
    
    # Left border width
    left_width = 0
    for col in arr.T:
        if np.all(col == 0):
            left_width += 1
        else:
            break
    
    # Right border width
    right_width = 0
    for col in arr.T[::-1]:
        if np.all(col == 0):
            right_width += 1
        else:
            break
    
    if proportion:
        return top_width / arr.shape[0], bottom_width / arr.shape[0], left_width / arr.shape[1], right_width / arr.shape[1]
    else:
        return top_width, bottom_width, left_width, right_width

def get_overlaps(image, borders_widths_prop, overlap_factor=0.2):
    """
    Compute the overlap dimensions for image cropping.

    Parameters:
        image (np.ndarray): Input image array.
        borders_widths_prop (tuple): Proportions of border widths (top, bottom, left, right).
        overlap_factor (float, optional): Factor to adjust the overlap. Defaults to 0.2.

    Returns:
        tuple: Overlap dimensions (overlap_x, overlap_y).
    """
    def compute_overlap(width_proportion, axis: int, overlap_factor: float):
        return int(width_proportion * image.shape[axis] * (1 + overlap_factor))

    def define_overlap(border1, border2, default_value):
        if border1 != border2:
            return max(border1, border2)
        return default_value

    # Compute overlaps
    top = compute_overlap(borders_widths_prop[0], axis=0, overlap_factor=overlap_factor)
    bottom = compute_overlap(borders_widths_prop[1], axis=0, overlap_factor=overlap_factor)
    left = compute_overlap(borders_widths_prop[2], axis=1, overlap_factor=overlap_factor)
    right = compute_overlap(borders_widths_prop[3], axis=1, overlap_factor=overlap_factor)

    # Define final overlaps
    overlap_x = define_overlap(left, right, image.shape[1] * 0.1)
    overlap_y = define_overlap(top, bottom, image.shape[0] * 0.1)

    return overlap_x, overlap_y

def estimate_overlap(fixed_image: np.ndarray, moving_image: np.ndarray, size: int = 500, overlap_factor=0.2):
    """
    Estimate the overlap between a fixed image and a moving image.

    Parameters:
        fixed_image (np.ndarray): The fixed image.
        moving_image (np.ndarray): The moving image.
        size (int, optional): Size of the crop for overlap estimation. Defaults to 500.
        overlap_factor (float, optional): Factor to adjust the overlap. Defaults to 0.2.

    Returns:
        tuple: Estimated overlap dimensions (overlap_x, overlap_y).
    """    
    fixed_crop = crop_2d_array(fixed_image, crop_areas=(0, size, 0, size))
    mov_crop = crop_2d_array(moving_image, crop_areas=(0, size, 0, size))

    affine_mapping = compute_affine_mapping_cv2(fixed_crop, mov_crop)
    reg_crop = apply_mapping(affine_mapping, mov_crop, method='cv2')[:, :, 2]

    borders_widths_prop = compute_border_width(reg_crop, proportion=True)

    overlap_x, overlap_y  = get_overlaps(fixed_image, borders_widths_prop, overlap_factor)

    return overlap_x, overlap_y

def estimate_overlap_2(fixed_image: np.ndarray, moving_image: np.ndarray, size: int = 500):
    """
    Estimate the overlap between a fixed image and a moving image.

    Parameters:
        fixed_image (np.ndarray): The fixed image.
        moving_image (np.ndarray): The moving image.
        size (int, optional): Size of the crop for overlap estimation. Defaults to 500.
        overlap_factor (float, optional): Factor to adjust the overlap. Defaults to 0.2.

    Returns:
        tuple: Estimated overlap dimensions (overlap_x, overlap_y).
    """    
    fixed_crop = crop_2d_array(fixed_image, crop_areas=(0, size, 0, size))
    mov_crop = crop_2d_array(moving_image, crop_areas=(0, size, 0, size))

    affine_mapping = compute_affine_mapping_cv2(fixed_crop, mov_crop)
    reg_crop = apply_mapping(affine_mapping, mov_crop, method='cv2')[:, :, 2]

    top_width, bottom_width, left_width, right_width = compute_border_width(reg_crop, proportion=False)

    return top_width, bottom_width, left_width, right_width

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

    if isinstance(crop_areas, list):
        if crop_indices is None:
            return [crop_area(area) for area in crop_areas]
        else:
            return [(idx, crop_area(area)) for idx, area in zip(crop_indices, crop_areas)]
    else:
        return crop_area(crop_areas)

def get_cropping_positions(image: np.ndarray, crop_width: int, overlap: int, axis=0):
    """
    Calculate the cropping positions for an image along a specified axis.

    Parameters:
        image (np.ndarray): The input 2D array representing the image to be cropped. Shape is (n_rows, n_cols).
        crop_width (int): The width of each crop.
        overlap (int): The number of columns that each crop should overlap with the previous one.
        axis (int, optional): The axis along which to calculate the positions. 0 for columns, 1 for rows. Defaults to 0.

    Returns:
        np.ndarray: A 2D array where the first row contains the starting indices and the second row contains the ending indices for each crop.
    """
    if crop_width <= overlap:
        raise ValueError("Crop width must be greater than overlap.")
    
    dim = image.shape[1] if axis == 0 else image.shape[0]
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

def get_crop_areas(image: np.ndarray, crop_width_x: int, crop_width_y: int, overlap_x: int, overlap_y: int, get_indices=True):
    """
    Calculate the crop areas for an image.

    Parameters:
        image (np.ndarray): The input image array.
        crop_width_x (int): Width of each crop along the x-axis.
        crop_width_y (int): Width of each crop along the y-axis.
        overlap_x (int): Overlap along the x-axis.
        overlap_y (int): Overlap along the y-axis.
        get_indices (bool, optional): Whether to return crop indices. Defaults to True.

    Returns:
        tuple: Crop indices and crop areas, or only crop areas if get_indices is False.
    """
    vertical_positions = get_cropping_positions(image, overlap=overlap_x, crop_width=crop_width_x, axis=0)
    horizontal_positions = get_cropping_positions(image, overlap=overlap_y, crop_width=crop_width_y, axis=1)
    crop_indices, crop_areas = make_crop_areas_list(horizontal_positions, vertical_positions)

    if get_indices:
        return crop_indices, crop_areas
    else:
        return crop_areas

def crop_2d_array_grid(image, crop_width_x: int = None, crop_width_y: int = None, overlap_x: int = None, overlap_y: int = None):
    """
    Crop an image into a grid of smaller images with specified overlap.

    Parameters:
        image (np.ndarray): The input 2D array representing the image to be cropped.
        crop_width_x (int, optional): Width of each crop along the x-axis.
        crop_width_y (int, optional): Width of each crop along the y-axis.
        overlap_x (int, optional): Overlap along the x-axis.
        overlap_y (int, optional): Overlap along the y-axis.

    Returns:
        list: List of cropped arrays with their indices.
    """
    crop_indices, crop_areas = get_crop_areas(image, crop_width_x, crop_width_y, overlap_x, overlap_y, get_indices=True)
    crops = crop_2d_array(array=image, crop_areas=crop_areas, crop_indices=crop_indices)

    return crops
