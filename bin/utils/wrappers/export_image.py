#!/usr/bin/env python

import numpy as np
import tifffile as tiff

# from src.utils.image_stitching import stitch_registered_crops
from utils.image_stitching import stitch_registered_crops

def export_image(registered_crops, overlap_x, overlap_y, output_path):
    """
    Export stitched image from registered crops to OME-TIFF format.

    Parameters:
        registered_crops (list): List of tuples containing indices and registered crop data.
        overlap_x (int): Overlap along x-axis between crops.
        overlap_y (int): Overlap along y-axis between crops.
        output_path (str): File path to save the stitched image.

    Returns:
        None
    """
    channels = np.max([idx[2] for idx, crop in registered_crops]) + 1
    stitched_channels = []

    for ch in range(channels):
        reg_channel = [(idx, crop) for idx, crop in registered_crops if idx[2] == ch]
        stitched = stitch_registered_crops(reg_channel, overlap_x=overlap_x, overlap_y=overlap_y)
        stitched_channels.append(stitched)

    # Combine stitched channels into a single 3D array
    stitched_image = np.stack(stitched_channels, axis=-1)

    # Save to OME-TIFF
    tiff.imwrite(output_path, stitched_image, imagej=True, metadata={'axes': 'ZYX'})
