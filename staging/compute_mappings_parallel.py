import os
from concurrent.futures import ProcessPoolExecutor
import pickle
 
# Define a function that performs the work for each crop
def process_crop(i, crop, fixed_crop_dapi, mov_crop_dapi, checkpoint_dir):
    mapping_affine = compute_affine_mapping_cv2(fixed_crop_dapi, mov_crop_dapi)
    affine1 = apply_mapping(mapping_affine, mov_crop_dapi, method='cv2')
    mapping_diffeomorphic = compute_diffeomorphic_mapping_dipy(fixed_crop_dapi, affine1)
    # Save the computed mappings
    save_pickle((mapping_affine, mapping_diffeomorphic), checkpoint_path)
    print(f"Saved checkpoint for i={crop[0][0]}_{crop[0][1]}")
 
    return (mapping_affine, mapping_diffeomorphic)
 
# Main function to parallelize the work
def process_all_crops(fixed_crops, checkpoint_dir, num_workers=4):
    mappings = []
    # Use ProcessPoolExecutor to parallelize the processing
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Prepare the tasks
        futures = []
        for i, crop in enumerate(fixed_crops):
            fixed_crop_dapi = fixed_crops[i][1][:, :, 2]
            mov_crop_dapi = moving_crops[i][1][:, :, 2]
            futures.append(executor.submit(process_crop, i, crop, fixed_crop_dapi, mov_crop_dapi, checkpoint_dir))
 
        # Collect the results as they complete
        for future in futures:
            mappings.append(future.result())
 
    return mappings
 
# Example usage
# mappings = process_all_crops(fixed_crops, checkpoint_dir, num_workers=4)