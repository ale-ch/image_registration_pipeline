import os

# from src.utils.image_mapping import apply_mapping
# from src.utils.pickle_utils import load_pickle, save_pickle

from utils.image_mapping import apply_mapping
from utils.pickle_utils import load_pickle, save_pickle

def apply_mappings(mappings, moving_crops, checkpoint_dir):
    """
    Apply affine and diffeomorphic mappings to a set of image crops and save/load results from checkpoints.

    Parameters:
        mappings (list): List of tuples containing affine and diffeomorphic mappings.
        moving_crops (list): List of tuples containing crop indices and image data.
        checkpoint_dir (str): Directory to save/load checkpoint files.

    Returns:
        list: List of tuples containing crop indices and the registered image data.
    """
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
        
    registered_crops = []
    channels = moving_crops[0][1].shape[2]

    for i, (mapping_affine, mapping_diffeo) in enumerate(mappings):
        for ch in range(channels):
            mov_crop = moving_crops[i][1][:, :, ch]
            mov_crop_idx = moving_crops[i][0]

            checkpoint_filename = os.path.join(checkpoint_dir, f'registered_split_{mov_crop_idx[0]}_{mov_crop_idx[1]}_{ch}.pkl')
            
            if os.path.exists(checkpoint_filename):
                # Load checkpoint if it exists
                checkpoint_data = load_pickle(checkpoint_filename)
                registered_crops.append((checkpoint_data[0], checkpoint_data[1]))
                print(f"Loaded checkpoint for i={mov_crop_idx}")
                continue

            affine2 = apply_mapping(mapping_affine, mov_crop, method='cv2')
            diffeo1 = apply_mapping(mapping_diffeo, affine2, method='dipy')
            
            # Save checkpoint
            checkpoint_data = (mov_crop_idx + (ch,), diffeo1)
            save_pickle(checkpoint_data, checkpoint_filename)
            print(f"Saved checkpoint for i={mov_crop_idx}")
            
            registered_crops.append(checkpoint_data)
    
    return registered_crops
