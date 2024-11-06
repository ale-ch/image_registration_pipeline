import os
import argparse
import numpy as np
import re
import h5py
import gc
import tifffile as tiff
import logging
from utils.io import save_h5, load_h5
from datetime import datetime
from utils import logging_config

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def log_file_size(path):
    """Print the current file size in bytes"""
    file_size = os.path.getsize(path)
    logger.info("Before opening the file:")
    logger.info(f"File size: {file_size} bytes")

def list_files_recursive(directory):
    paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            paths.append(os.path.join(root, file))            
    return paths

def extract_date_from_path(path):
    match = re.search(r'\d{4}\.\d{2}\.\d{2}', path)  # Find YYYY.MM.DD pattern
    if match:
        return datetime.strptime(match.group(), '%Y.%m.%d')  # Convert to datetime
    return None

def load_h5_channels(path, channels_to_load):
    # Open the HDF5 file
    with h5py.File(path, 'r') as f:
        # Access the dataset
        dataset = f['dataset']
        # Use slicing to load only the specific channels
        data = dataset[:, :, channels_to_load]
    
        return data

def stack_channel(file_path, new_channel_data):
    """
    Append a new channel to an existing dataset in an HDF5 file without loading the entire dataset into memory.
    
    Args:
        file_path (str): Path to the HDF5 file.
        new_channel_data (numpy.ndarray): The new channel data to be added. 
                                           It should have the shape (n, m, 1) where (n, m) matches the existing dataset dimensions.
    """
    with h5py.File(file_path, 'a') as hdf_file:
        # Access the existing dataset
        dataset = hdf_file['dataset']
        
        # Check the current shape of the dataset
        current_shape = dataset.shape
        n, m, c = current_shape  # Unpack current dimensions
        
        # Create a new shape for the dataset with an additional channel
        new_shape = (n, m, c + 1)
        
        # Resize the dataset to accommodate the new channel
        dataset.resize(new_shape)

        # Add the new channel data to the last channel of the dataset
        dataset[:, :, -1] = new_channel_data

def main(args):
    filename = os.path.basename(args.fixed_image_path).split('_')[0]
    output_path = os.path.join(args.output_dir, f'{filename}.h5') # Path to output file

    # Load current fixed image
    fixed_image = load_h5(args.fixed_image_path)
    # Save transposed fixed image: (n, m, c) --> (c, n, m)
    save_h5(np.transpose(fixed_image, (2, 0, 1)), output_path, chunks=True)

    del fixed_image
    gc.collect()

    #### Channels stacking ####
    file_paths = [file for file in list_files_recursive(args.output_dir) if file.endswith('.h5')]
    sorted_files = sorted(file_paths, key=extract_date_from_path)
    n_channels = 2

    # Channel stacking loop
    for file in sorted_files:
        for ch in range(n_channels):
            # Load individual channel and transpose it
            new_channel = np.transpose(np.squeeze(load_h5_channels(file, [ch])), (2, 0, 1)) 
            log_file_size(output_path)

            # Stack channel to fixed image
            stack_channel(output_path, new_channel)
    
    # Save stacked image as tiff
    stacked_image = load_h5(output_path)
    output_path_tiff = output_path.replace('h5', 'tiff')
    tiff.imwrite(output_path_tiff, stacked_image)

    del stacked_image
    gc.collect()
    
    #### Channels logging ####
    fixed_channels = os.path.basename(args.fixed_image_path.replace('.h5', '')).split('_')[1:4][::-1]
    channels = [os.path.basename(file.replace('.h5', '')) for file in sorted_files]
    channels = [file.split('_')[2:4][::-1] for file in channels].insert(0, fixed_channels)
    channels = [item for sublist in channels for item in sublist]

    channels_log_path = os.path.join(args.logs_dir, f'channels_log_{filename}.txt')
    with open(channels_log_path, 'w') as f:
        # Write the header line
        f.write(f"Patient id: {filename}\n\n")  # Two newlines for spacing, optional

        # Write each item with "Channel X" format
        for index, item in enumerate(channels, start=1):
            f.write(f"Channel {index}: {item}\n")

    print(f"Data has been written to {channels_log_path}")
 
        
if __name__ == '__main__':
    # Set up argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--output-dir', type=str, required=True, 
                        help='Path to save the registered image.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to the fixed image used for registration.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to the directory where log files will be stored.')
    
    args = parser.parse_args()
    main(args)
