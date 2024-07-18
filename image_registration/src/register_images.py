import argparse
import os 
from skimage.io import imread 
from src.utils.image_cropping import estimate_overlap
from src.utils.image_cropping import crop_2d_array_grid
from src.utils.image_loading import get_fixed_image_path
from src.utils.image_loading import read_paths_from_file
from src.utils.image_loading import match_pattern_str_list
from src.utils.image_loading import make_paths_from_matches
from src.utils.image_loading import get_leaf_directory
from src.utils.image_loading import filter_elements
from src.utils.wrappers.create_checkpoint_dirs import create_checkpoint_dirs
from src.utils.wrappers.compute_mappings import compute_mappings
from src.utils.wrappers.apply_mappings import apply_mappings
from src.utils.wrappers.export_image import export_image
from src.utils.empty_folder import empty_folder

def get_paths_to_process(cur_logs_dir):
    # Get paths to files in cur_logs_dir
    cur_input_match = match_pattern_str_list(os.listdir(cur_logs_dir), 'input')
    cur_output_match = match_pattern_str_list(os.listdir(cur_logs_dir), 'output')
    cur_input_file_path = make_paths_from_matches(cur_logs_dir, cur_input_match)
    cur_output_file_path = make_paths_from_matches(cur_logs_dir, cur_output_match)
    # Read in the files
    input_paths_raw = read_paths_from_file(cur_input_file_path)
    output_paths_raw = read_paths_from_file(cur_output_file_path)
    # Filter out directories with less than two elements
    input_dirs = list(set([get_leaf_directory(path) for path in input_paths_raw]))
    target_input_dirs = [dir for dir in input_dirs if len(os.listdir(dir)) > 1]
    input_paths = filter_elements(target_input_dirs, input_paths_raw)
    output_paths = filter_elements(target_input_dirs, output_paths_raw)

    return input_paths, output_paths

def register_images(cur_logs_dir, root_mappings_dir, root_registered_crops_dir, fixed_image_pattern,  
                    crop_width_x, crop_width_y, overlap_factor=0.3, delete_checkpoints=False):
    # Get input and output paths
    input_paths, output_paths = get_paths_to_process(cur_logs_dir)

    # Get fixed and moving images paths
    fixed_image_path, moving_images_paths = get_fixed_image_path(input_paths, pattern=fixed_image_pattern)
    _, output_paths = get_fixed_image_path(output_paths)

    # Load the fixed image
    fixed_image = imread(fixed_image_path)

    for moving_image_path, output_path in zip(moving_images_paths, output_paths):
        print(f'Input path: {moving_image_path}')
        print(f'Output path: {output_path}')
        moving_image = imread(moving_image_path)

        current_mappings_dir, current_registered_crops_dir = create_checkpoint_dirs(root_mappings_dir, root_registered_crops_dir, moving_image_path)

        overlap_x, overlap_y = estimate_overlap(fixed_image, moving_image, overlap_factor=overlap_factor)
        fixed_crops = crop_2d_array_grid(fixed_image, crop_width_x, crop_width_y, overlap_x, overlap_y)
        moving_crops = crop_2d_array_grid(moving_image, crop_width_x, crop_width_y, overlap_x, overlap_y)

        mappings = compute_mappings(fixed_crops=fixed_crops, moving_crops=moving_crops, checkpoint_dir=current_mappings_dir)
        registered_crops = apply_mappings(mappings=mappings, moving_crops=moving_crops, checkpoint_dir=current_registered_crops_dir)
        export_image(registered_crops, overlap_x, overlap_y, output_path)
        print('Image processed successfully.')

        if delete_checkpoints:
            empty_folder(current_mappings_dir)
            print(f'Content deleted successfully: {current_mappings_dir}')
            empty_folder(current_registered_crops_dir)
            print(f'Content deleted successfully: {current_registered_crops_dir}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--cur-logs-dir', type=str, help='Path to the directory with the current input and output log files.')
    parser.add_argument('--root-mappings-dir', type=str, help='Root directory to save mappings.')
    parser.add_argument('--root-registered_crops-dir', type=str, help='Root directory to save registered crops.')
    parser.add_argument('--fixed-image-pattern', type=str, help='File name pattern identifying the fixed image.')
    parser.add_argument('--crop-width-x', type=int, help='Crop width.')
    parser.add_argument('--crop-width-y', type=int, help='Crop height.')
    parser.add_argument('--overlap-factor', type=float, help='Percentage by which the estimated overlap should be increased by.')
    parser.add_argument('--delete-checkpoints', type=bool, help='Delete image mappings and registered crops files after processing.')

    args = parser.parse_args()
    
    register_images(args.cur_logs_dir, args.root_mappings_dir, args.root_registered_crops_dir, args.fixed_image_pattern, \
                    args.crop_width_x, args.crop_width_y, args.overlap_factor, args.delete_checkpoints)
