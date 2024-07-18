import itertools
import numpy as np

def remove_crops_overlap(crops: list, overlap: int, axis: int = 0):
    """
    Remove overlapping regions from adjacent crops along a specified axis.

    Args:
        crops (list): List of tuples where each tuple contains an index and a 2D numpy array.
                      The index tuple consists of (row, column, image channel).
        overlap (int): Size of overlap between adjacent crops.
        axis (int): Axis along which to remove the overlap:
                    - 0 for rows
                    - 1 for columns

    Returns:
        list: List of tuples containing the adjusted crops without overlaps.
    """
    overlap_half_left = overlap // 2
    overlap_half_right = overlap - overlap_half_left
    crops_no_overlap = []

    # Sort crops by row and then by column
    crops = sorted(crops, key=lambda x: (x[0][0], x[0][1]))

    for idx, crop in crops:
        start_row, end_row, start_col, end_col = 0, crop.shape[0], 0, crop.shape[1]

        # Handle row overlap
        if axis == 0:
            if idx[0] != 0:
                start_row += overlap_half_left
            if idx[0] != max(idx[0] for idx, _ in crops):
                end_row -= overlap_half_right

        # Handle column overlap
        if axis == 1:
            if idx[1] != 0:
                start_col += overlap_half_left
            if idx[1] != max(idx[1] for idx, _ in crops):
                end_col -= overlap_half_right

        # Extract the crop area without overlap
        crop_no_overlap = crop[start_row:end_row, start_col:end_col]

        # Append the non-overlapping crop to the list
        crops_no_overlap.append((idx, crop_no_overlap))
    
    return crops_no_overlap


def get_stitching_positions(crops: list):
    """
    Calculate the positions where each cropped image will be placed in the final stitched image.

    Args:
        crops (list): List of tuples where each tuple contains an index and a 2D numpy array 
                      representing the cropped image. The index tuple consists of (row, column, image channel).

    Returns:
        list: A list of (row, col) positions where each crop will be placed in the final stitched image.
    """
    # Determine the number of crop rows and columns
    n_crop_rows = np.max([element[0][0] for element in crops]) + 2
    n_crop_cols = np.max([element[0][1] for element in crops]) + 2

    # Calculate row stitching positions
    sorted_crops = sorted(crops, key=lambda x: x[0][1])
    if n_crop_rows - 1 > 1:
        crops_rows = [crop.shape[0] for idx, crop in sorted_crops][:n_crop_rows - 2]
    else:
        crops_rows = [crop.shape[0] for idx, crop in sorted_crops][:n_crop_rows - 1]

    crops_rows = np.insert(crops_rows, 0, 0)
    stitching_positions_h = np.cumsum(crops_rows)

    # Calculate column stitching positions
    sorted_crops = sorted(crops, key=lambda x: x[0][0])
    if n_crop_cols - 1 > 1:
        crops_cols = [crop.shape[1] for idx, crop in sorted_crops][:n_crop_cols - 2]
    else:
        crops_cols = [crop.shape[1] for idx, crop in sorted_crops][:n_crop_cols - 1]

    crops_cols = np.insert(crops_cols, 0, 0)
    stitching_positions_v = np.cumsum(crops_cols)

    # Generate stitching positions
    stitching_positions = list(itertools.product(stitching_positions_h, stitching_positions_v))

    return stitching_positions


def stitch_images(rectangles: list, positions: list):
    """
    Stitches an array of rectangular images of variable sizes into a single large image.

    Parameters:
        rectangles (list of np.array): List of rectangular images to be stitched.
        positions (list of tuple): List of (row, col) positions where each rectangle will be 
                                   placed in the final image.

    Returns:
        np.array: The stitched image.
    """
    # Determine the size of the final stitched image
    max_height = 0
    max_width = 0
    
    for rectangle, (row, col) in zip(rectangles, positions):
        height, width = rectangle.shape[:2]
        max_height = max(max_height, row + height)
        max_width = max(max_width, col + width)
    
    # Initialize an empty array for the stitched image
    stitched_image = np.zeros((max_height, max_width), dtype=rectangles[0].dtype)
    
    for rectangle, (row, col) in zip(rectangles, positions):
        height, width = rectangle.shape[:2]
        stitched_image[row:row + height, col:col + width] = rectangle
    
    return stitched_image


def stitch_registered_crops(images, overlap_x: int, overlap_y: int):
    """
    Stitches registered image crops into a single image after removing overlaps.

    Parameters:
        images (list of tuples): List of tuples where each tuple contains an index and a 2D 
                                 numpy array representing the cropped image. The index tuple 
                                 consists of the (row, column, image channel).
        overlap_x (int): Overlap to be removed along the x-axis (columns).
        overlap_y (int): Overlap to be removed along the y-axis (rows).

    Returns:
        np.array: The stitched image after removing overlaps.
    """
    # Sanity check: Ensure overlap values are non-negative
    if overlap_x < 0 or overlap_y < 0:
        raise ValueError("Overlap values must be non-negative.")

    # Remove overlap along columns
    crops_no_overlap = remove_crops_overlap(crops=images, overlap=overlap_x, axis=1) 
    
    # Remove overlap along rows
    crops_no_overlap = remove_crops_overlap(crops=crops_no_overlap, overlap=overlap_y, axis=0) 

    stitching_positions = get_stitching_positions(crops_no_overlap)
    stitched = stitch_images([crop for idx, crop in crops_no_overlap], stitching_positions)

    return stitched
