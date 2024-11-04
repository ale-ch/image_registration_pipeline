#!/usr/bin/env python

import numpy as np
from .io_tools import load_pickle
from .misc import get_indexed_filepaths
from concurrent.futures import ProcessPoolExecutor

def stitch_rectangle(stitched_image: np.array, rectangle: np.array, position: tuple):
    """
    Stitches one rectangle into its position in the pre-initialized stitched image.
    
    Parameters:
        stitched_image (np.array): The pre-initialized stitched image.
        rectangle (np.array): The current rectangle to be stitched.
        position (tuple): A tuple (row, col) indicating where to place the rectangle.
    
    Returns:
        np.array: The updated stitched image with the new rectangle stitched in place.
    """
    row, col = position
    height, width = rectangle.shape[:2]
    
    # Place the rectangle in the specified position
    stitched_image[row:row + height, col:col + width] = rectangle
    
    return stitched_image

def process_stitch_channel(paths, positions, shape):
    stitched_image = np.zeros(shape, dtype='uint16')
    for path, position in zip(paths, positions):
        crop = load_pickle(path)
        stitched_image = stitch_rectangle(stitched_image, crop[1], position)
    return stitched_image

def stitch_crops(crops_dir, shape, positions, max_workers):
    crops_paths = get_indexed_filepaths(crops_dir)
    n_channels = 3
    stitched_images = []
    
    # Create a ProcessPoolExecutor to parallelize stitching across channels
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for ch in range(n_channels):
            # Get the paths corresponding to the current channel
            paths = [path[1] for path in crops_paths if path[0][2] == ch]
            
            # Submit the stitching task for each channel
            futures.append(executor.submit(process_stitch_channel, paths, positions, shape))
        
        # Collect the stitched images for each channel as the tasks complete
        for future in futures:
            stitched_images.append(future.result())
    
    # Stack the stitched images along the channel axis to form the final image
    return np.stack(stitched_images, axis=-1)
