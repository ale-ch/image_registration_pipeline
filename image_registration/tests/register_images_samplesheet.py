import argparse
import os 
import pathlib
from skimage.io import imread 
from utils.image_cropping import estimate_overlap
from utils.image_cropping import crop_2d_array_grid
from utils.wrappers.create_checkpoint_dirs import create_checkpoint_dirs
from utils.wrappers.compute_mappings import compute_mappings
from utils.wrappers.apply_mappings import apply_mappings
from utils.wrappers.export_image import export_image
from utils.empty_folder import empty_folder

def register_images(sample_sheet, mappings_dir, registered_crops_dir,  
                    crop_width_x, crop_width_y, overlap_factor=0.3, delete_checkpoints=False):
    for i, row in sample_sheet.iterrows():
        input_path = row['input_path']
        output_path = row['output_path']
        fixed_image_path = row['fixed_image_path']

        print(f'Output path: {output_path}')
        fixed_image = imread(fixed_image_path)
        moving_image = imread(input_path)
        
        overlap_x, overlap_y = estimate_overlap(fixed_image, moving_image, overlap_factor=overlap_factor)
        fixed_crops = crop_2d_array_grid(fixed_image, crop_width_x, crop_width_y, overlap_x, overlap_y)
        moving_crops = crop_2d_array_grid(moving_image, crop_width_x, crop_width_y, overlap_x, overlap_y)

        current_mappings_dir, current_registered_crops_dir = create_checkpoint_dirs(mappings_dir, registered_crops_dir, input_path)
        mappings = compute_mappings(fixed_crops=fixed_crops, moving_crops=moving_crops, checkpoint_dir=current_mappings_dir)
        registered_crops = apply_mappings(mappings=mappings, moving_crops=moving_crops, checkpoint_dir=current_registered_crops_dir)
        export_image(registered_crops, overlap_x, overlap_y, output_path)
        print('Image processed successfully.')

        if delete_checkpoints:
            empty_folder(current_mappings_dir)
            print(f'Content deleted successfully: {current_mappings_dir}')
            empty_folder(current_registered_crops_dir)
            print(f'Content deleted successfully: {current_registered_crops_dir}')