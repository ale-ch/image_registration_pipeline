#!/usr/bin/env python

import os
from utils.pickle_utils import save_pickle, load_pickle
from utils.image_mapping import apply_mapping

def apply_mappings(mappings, moving_crops, method='dipy', checkpoint_dir=None):
    """
    Apply affine and diffeomorphic mappings to a set of image crops and save/load results from checkpoints.

    Parameters:
        mappings (list): List of tuples containing affine and diffeomorphic mappings.
        moving_crops (list): List of tuples containing crop indices and image data.
        method (str): The mapping method to use ('cv2' or 'dipy'). Default is 'dipy'.
        checkpoint_dir (str): Directory to save/load checkpoint files.

    Returns:
        list: List of tuples containing crop indices and the registered image data.
    """
    if checkpoint_dir is not None:
        # Create checkpoint directory if it doesn't exist
        os.makedirs(checkpoint_dir, exist_ok=True)
        
    registered_crops = []
    n_channels = moving_crops[0][1].shape[2]  # Assuming all crops have the same number of channels

    if method == 'cv2':
        # Apply cv2 mappings
        mapping = mappings  # Assuming 'mappings' is a direct mapping in cv2 case
        for i, crop in enumerate(moving_crops):
            for ch in range(n_channels):
                mov_crop = crop[1][:, :, ch]  # Extract the specific channel of the moving crop
                mov_crop_idx = crop[0]  # Get the index of the crop
        
                # Apply mappings
                mapped_image_indexed = (mov_crop_idx + (ch,), apply_mapping(mapping, mov_crop, method=method))
        
                registered_crops.append(mapped_image_indexed)

    elif method == 'dipy':
        # Apply dipy mappings
        for i, mapping in enumerate(mappings):
            for ch in range(n_channels):
                mov_crop = moving_crops[i][1][:, :, ch]  # Extract the specific channel of the moving crop
                mov_crop_idx = moving_crops[i][0]  # Get the index of the crop
    
                if checkpoint_dir is not None:
                    # Construct checkpoint filename
                    checkpoint_filename = os.path.join(checkpoint_dir, f'registered_split_{mov_crop_idx[0]}_{mov_crop_idx[1]}_{ch}.pkl')
                    
                    if os.path.exists(checkpoint_filename):
                        # Load checkpoint if it exists
                        mapped_image_indexed = load_pickle(checkpoint_filename)
                        print(f"Loaded checkpoint for i={mov_crop_idx}")
                        registered_crops.append(mapped_image_indexed)
                        continue
    
                # Apply mappings
                mapped_image_indexed = (mov_crop_idx + (ch,), apply_mapping(mapping, mov_crop, method=method))
    
                if checkpoint_dir is not None:
                    # Save checkpoint
                    save_pickle(mapped_image_indexed, checkpoint_filename)
                    print(f"Saved checkpoint for i={mov_crop_idx}")
    
    return registered_crops  # Return the registered crops
