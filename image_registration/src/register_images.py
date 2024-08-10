import argparse
import os 
import pathlib
import pandas as pd
import logging
from skimage.io import imread 
from utils.image_cropping import estimate_overlap
from utils.image_cropping import crop_2d_array_grid
from utils.wrappers.create_checkpoint_dirs import create_checkpoint_dirs
from utils.wrappers.compute_mappings import compute_mappings
from utils.wrappers.apply_mappings import apply_mappings
from utils.wrappers.export_image import export_image
from utils.empty_folder import empty_folder
from utils.image_loading import assign_fixed_image
from shared import logging_config

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def register_images(sample_sheet_path, mappings_dir, registered_crops_dir,  
                    crop_width_x, crop_width_y, overlap_x, overlap_y, 
                    auto_overlap, overlap_factor, delete_checkpoints):
    common_sample_sheet = pd.read_csv(sample_sheet_path)

    sample_sheet = assign_fixed_image(common_sample_sheet)
    sample_sheet = sample_sheet[sample_sheet['processed'] == False]
    sample_sheet = sample_sheet[sample_sheet['input_path'] != sample_sheet['fixed_image_path']]

    for i, row in sample_sheet.iterrows():
        input_path = row['input_path']
        output_path = row['output_path']
        fixed_image_path = row['fixed_image_path']

        logger.info(f'Output path: {output_path}')
        fixed_image = imread(fixed_image_path)
        moving_image = imread(input_path)
        
        if auto_overlap:
            overlap_x, overlap_y = estimate_overlap(fixed_image, moving_image, overlap_factor=overlap_factor)
        
        logger.debug(f"Overlap X: {overlap_x}")
        logger.debug(f"Overlap Y: {overlap_y}")

        fixed_crops = crop_2d_array_grid(fixed_image, crop_width_x, crop_width_y, overlap_x, overlap_y)
        moving_crops = crop_2d_array_grid(moving_image, crop_width_x, crop_width_y, overlap_x, overlap_y)

        current_mappings_dir, current_registered_crops_dir = create_checkpoint_dirs(mappings_dir, registered_crops_dir, input_path)
        mappings = compute_mappings(fixed_crops=fixed_crops, moving_crops=moving_crops, checkpoint_dir=current_mappings_dir)
        registered_crops = apply_mappings(mappings=mappings, moving_crops=moving_crops, checkpoint_dir=current_registered_crops_dir)
        export_image(registered_crops, overlap_x, overlap_y, output_path)
        logger.info(f'Image {input_path} processed successfully.')

        if delete_checkpoints:
            empty_folder(current_mappings_dir)
            logger.info(f'Content deleted successfully: {current_mappings_dir}')
            empty_folder(current_registered_crops_dir)
            logger.info(f'Content deleted successfully: {current_registered_crops_dir}')

def main(args):
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    register_images(args.sample_sheet_path, args.mappings_dir, args.registered_crops_dir,  \
                    args.crop_width_x, args.crop_width_y, args.overlap_x, args.overlap_y,
                    args.auto_overlap, args.overlap_factor, args.delete_checkpoints)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--sample-sheet-path', type=str, required=True, 
                        help='Path to sample sheet containing input-output pairs of paths to images.')
    parser.add_argument('--mappings-dir', type=str, required=True, 
                        help='Root directory to save mappings.')
    parser.add_argument('--registered-crops-dir', type=str, required=True, 
                        help='Root directory to save registered crops.')
    parser.add_argument('--crop-width-x', required=True, type=int, 
                        help='Crop width.')
    parser.add_argument('--crop-width-y', required=True, type=int, 
                        help='Crop height.')
    parser.add_argument('--overlap-x', type=int, 
                        help='Overlap of each crop along x axis.')
    parser.add_argument('--overlap-y', type=int, 
                        help='Overlap of each crop along y axis.')
    parser.add_argument('--auto-overlap', action='store_false', 
                        help='Automatically estimate overlap along both x and y axes.')
    parser.add_argument('--overlap-factor', type=float, 
                        help='Percentage by which the estimated overlap should be increased by.')
    parser.add_argument('--delete-checkpoints', action='store_false', 
                        help='Delete image mappings and registered crops files after processing.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to directory where log files will be stored.')

    args = parser.parse_args()
    
    main(args)
    
