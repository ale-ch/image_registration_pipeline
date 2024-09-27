#!/usr/bin/env python

import gc
import numpy as np
import tifffile as tiff
from utils.image_stitching import stitch_registered_crops

def export_image(registered_crops, overlap_x, overlap_y, output_path: str = None, export: bool = True):
    """
    Export stitched image from registered crops to OME-TIFF format.

    Parameters:
        registered_crops (list): List of tuples containing indices and registered crop data.
        overlap_x (int): Overlap along x-axis between crops.
        overlap_y (int): Overlap along y-axis between crops.
        output_path (str): File path to save the stitched image. If None, the image will not be saved.
        export (bool): Flag indicating whether to save the image to file.

    Returns:
        np.ndarray: The stitched image array.
    """
    # Determine the number of channels
    channels = np.max([idx[2] for idx, _ in registered_crops]) + 1
    stitched_channels = []

    for ch in range(channels):
        # Filter registered crops for the current channel
        reg_channel = [(idx, crop) for idx, crop in registered_crops if idx[2] == ch]
        
        # Stitch the crops for the current channel
        stitched = stitch_registered_crops(reg_channel, overlap_x=overlap_x, overlap_y=overlap_y)
        
        # Clean up to free memory
        del reg_channel
        gc.collect()
        
        stitched_channels.append(stitched)

        # Clean up to free memory after stitching
        del stitched
        gc.collect()

    # Combine stitched channels into a single 3D array
    stitched_image = np.stack(stitched_channels, axis=-1)

    # Clean up to free memory before returning
    del stitched_channels
    gc.collect()

    # Save to OME-TIFF file if the export flag is set to True
    if export and output_path is not None:
        tiff.imwrite(output_path, stitched_image, imagej=True, metadata={'axes': 'ZYX'})
    elif output_path is None:
        print("Output path is None; image will not be saved.")

    return stitched_image
