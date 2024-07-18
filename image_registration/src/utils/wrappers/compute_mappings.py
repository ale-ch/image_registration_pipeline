import os

from src.utils.pickle_utils import load_pickle, save_pickle
from src.utils.image_mapping import apply_mapping, compute_affine_mapping_cv2, compute_diffeomorphic_mapping_dipy

def compute_mappings(fixed_crops, moving_crops, checkpoint_dir):
    """
    Compute affine and diffeomorphic mappings between fixed and moving image crops and save/load results from checkpoints.

    Parameters:
        fixed_crops (list): List of tuples containing crop indices and fixed image data.
        moving_crops (list): List of tuples containing crop indices and moving image data.
        checkpoint_dir (str): Directory to save/load checkpoint files.

    Returns:
        list: List of tuples containing affine and diffeomorphic mappings.
    """
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
    
    mappings = []
    for i, crop in enumerate(fixed_crops):
        checkpoint_path = os.path.join(checkpoint_dir, f'mapping_{crop[0][0]}_{crop[0][1]}.pkl')
        
        if os.path.exists(checkpoint_path):
            # Load mapping from checkpoint if it exists
            mapping_affine, mapping_diffeomorphic = load_pickle(checkpoint_path)
        else:
            fixed_crop_dapi = fixed_crops[i][1][:, :, 2]
            mov_crop_dapi = moving_crops[i][1][:, :, 2]

            mapping_affine = compute_affine_mapping_cv2(fixed_crop_dapi, mov_crop_dapi)
            affine1 = apply_mapping(mapping_affine, mov_crop_dapi, method='cv2')
            mapping_diffeomorphic = compute_diffeomorphic_mapping_dipy(fixed_crop_dapi, affine1)
            
            # Save the computed mappings
            save_pickle((mapping_affine, mapping_diffeomorphic), checkpoint_path)
        
        mappings.append((mapping_affine, mapping_diffeomorphic))
    
    return mappings
