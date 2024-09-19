#!/usr/bin/env python

import numpy as np
import gc
from utils.image_cropping import crop_2d_array_grid
from utils.image_cropping import get_crop_areas
from utils.image_mapping import compute_affine_mapping_cv2
from utils.wrappers.apply_mappings import apply_mappings
from utils.wrappers.export_image import export_image

def get_cropping_params(image):
    shape = image.shape
    
    if shape[0] > 64000:
        crop_fraction_y = 3
    else:
        crop_fraction_y = 2
    
    if shape[1] > 64000:
        crop_fraction_x = 3
    else:
        crop_fraction_x = 2
    
    crop_width_y = shape[0] // crop_fraction_y
    crop_width_x = shape[1] // crop_fraction_x
    overlap_y = crop_width_y // 2
    overlap_x = crop_width_x // 2

    return crop_width_x, crop_width_y, overlap_x, overlap_y

def get_dense_crops(moving, fixed, crop_width_x, crop_width_y, overlap_x, overlap_y):
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

def affine_registration(fixed, moving, crop=True, crop_size=4000, n_features=2000):
    crop_width_x, crop_width_y, overlap_x, overlap_y = get_cropping_params(fixed)

    fixed_crop, moving_crop = get_dense_crops(moving, fixed, crop_width_x, crop_width_y, overlap_x, overlap_y)
    
    matrix = compute_affine_mapping_cv2(fixed_crop[:,:,2], moving_crop[:,:,2], crop, crop_size, n_features)
    
    del fixed_crop, moving_crop
    gc.collect()
    
    crops = crop_2d_array_grid(image=moving, crop_width_x=crop_width_x, crop_width_y=crop_width_y, overlap_x=overlap_x, overlap_y=overlap_y)
    
    del moving
    gc.collect()
    
    mapped_crops = apply_mappings(matrix, crops, 'cv2')
    
    del crops
    gc.collect()
    
    stitched_image = export_image(mapped_crops, overlap_x, overlap_y, export=False)
    
    del mapped_crops
    gc.collect()

    return stitched_image