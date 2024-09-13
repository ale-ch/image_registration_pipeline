import tifffile as tiff
import pandas as pd
import numpy as np
import nd2
import argparse

# Function to get image shape from an .nd2 file
def get_nd2_shape(path):
    with nd2.ND2File(path) as nd2_file:
        return nd2_file.shape  # Returns shape as (z, y, x) or (y, x)
    
# Function to get fixed image's start/end row/column per group
def apply_fixed_image_values(group):
    fixed_image_row = group[group['fixed_image']].iloc[0]
    group['start_row_fixed'] = fixed_image_row['start_row']
    group['end_row_fixed'] = fixed_image_row['end_row']
    group['start_col_fixed'] = fixed_image_row['start_col']
    group['end_col_fixed'] = fixed_image_row['end_col']
    return group

# Function to calculate cropping areas for images based on the minimum shape_x and shape_y by patient_id
def get_regular_crop_areas(sample_sheet_path, ref_col='input_path_conv', group_col='patient_id'):
    # Load the CSV file and extract image paths along with patient IDs
    df = pd.read_csv(sample_sheet_path)
    image_paths = df[ref_col].tolist()
    patient_ids = df[group_col].tolist()

    # Get the shapes of all images (shape_x, shape_y)
    shapes = [get_nd2_shape(path) for path in image_paths]
    shape_x, shape_y = zip(*[(s[-2], s[-1]) for s in shapes])  # Extract x, y from the shape

    # Create a DataFrame with the image shapes and patient IDs
    df_shapes = pd.DataFrame({'patient_id': patient_ids, 'shape_x': shape_x, 'shape_y': shape_y})

    # Group by patient_id and find the minimum shape_x and shape_y for each patient
    df_min_shapes = df_shapes.groupby('patient_id').agg({
        'shape_x': 'min',
        'shape_y': 'min'
    }).reset_index()

    # Merge the minimum shapes back with the original data
    df_merged = pd.merge(df_shapes, df_min_shapes, on=group_col, suffixes=('', '_min'))

    # Calculate start_col, end_col, start_row, and end_row based on the minimum shape_x_min and shape_y_min
    df_merged['start_row'] = np.floor((df_merged['shape_y'] - df_merged['shape_y_min']) / 2).astype(int)
    df_merged['end_row'] = df_merged['shape_y'] - np.ceil((df_merged['shape_y'] - df_merged['shape_y_min']) / 2).astype(int)
    df_merged['start_col'] = np.floor((df_merged['shape_x'] - df_merged['shape_x_min']) / 2).astype(int)
    df_merged['end_col'] = df_merged['shape_x'] - np.ceil((df_merged['shape_x'] - df_merged['shape_x_min']) / 2).astype(int)

    # Select the final relevant columns
    df_result = df_merged[['start_row', 'end_row', 'start_col', 'end_col']]

    df_final = pd.concat([df.set_axis(df_result.index), df_result], axis=1)

    return df_final

# Main function to handle argument parsing
def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Calculate regular crop areas for .nd2 images based on the minimum shapes by patient_id.")
    parser.add_argument('--sample-sheet-path', type=str, help="Path to the CSV sample sheet.")
    parser.add_argument('--ref-col', type=str, default='input_path_conv', help="Column name in the sample sheet containing image paths.")
    parser.add_argument('--group-col', type=str, default='patient_id', help="Column name in the sample sheet containing patient IDs.")
    parser.add_argument('--export-path', type=str, required=True, help='Path where the filtered sample sheet will be saved.')

    # Parse arguments
    args = parser.parse_args()

    # Call the function with arguments
    result = get_regular_crop_areas(args.sample_sheet_path, ref_col=args.ref_col, group_col=args.group_col)

    # Apply function to each patient_id group
    result = result.groupby(args.group_col).apply(apply_fixed_image_values)
    result = result.reset_index(drop=True)

    # Save to csv file
    result.to_csv(args.export_path, index=False)

# Entry point for the script
if __name__ == "__main__":
    main()
