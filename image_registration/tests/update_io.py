import os
import re
import pandas as pd
import argparse

def list_files(directory):
    """
    List all files in a directory and its subdirectories.

    Args:
        directory (str): The directory to search for files.

    Returns:
        list: List of file paths.
    """
    paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            paths.append(os.path.join(root, file))
    return paths

def get_leaf_directory(path):
    """
    Get the leaf directory name from a given path.

    Args:
        path (str): The file path.

    Returns:
        str: The leaf directory name.
    """
    return os.path.basename(os.path.dirname(path))

def oldest_date_value(group):
    """
    Get the file path corresponding to the oldest date in the group.

    Args:
        group (pd.Series): The group of file paths.

    Returns:
        str: The file path with the oldest date.
    """
    if not group.empty:
        return group.loc[group['date'].idxmin(), 'input_path']
    return None

def get_base_directory_and_file(path):
    """
    Get the base directory and file name from a path.

    Args:
        path (str): The file path.

    Returns:
        str: The combined base directory and file name.
    """
    dir_name = os.path.basename(os.path.dirname(path))
    file_name = os.path.basename(path)
    return os.path.join(dir_name, file_name)

def remove_extension(filename):
        return re.sub(r'(\.\w+)+$', '', filename)

def generate_sample_sheet(input_dir, output_dir, input_ext='.nd2', output_ext='.nd2'):
    """
    Generate a sample sheet with input and output paths.

    Args:
        input_dir (str): The directory containing input files.
        output_dir (str): The directory to store output files.
        file_extension (str): The file extension to filter by.

    Returns:
        pd.DataFrame: The generated sample sheet.
    """
    input_paths = [path for path in list_files(input_dir) if path.endswith(input_ext)]
    patient_ids = [os.path.basename(path).split('_', 1)[0] for path in input_paths]
    sample_sheet = pd.DataFrame({'patient_id': patient_ids, 'input_path': input_paths})

    # Function to join dir_path with the filename
    def join_path(file_path):
        return os.path.join(output_dir, file_path)

    sample_sheet['base_dir'] = sample_sheet['input_path'].apply(get_base_directory_and_file)
    sample_sheet['output_path'] = sample_sheet['base_dir'].apply(join_path)
    sample_sheet.drop(columns=['base_dir'], inplace=True)
    sample_sheet['output_path'] = sample_sheet['output_path'].apply(remove_extension) + output_ext
    sample_sheet['processed'] = sample_sheet['output_path'].apply(lambda x: os.path.exists(x)) 

    print('Sample sheet generated successfully.')
    return sample_sheet

def get_fixed_image(sample_sheet):
    sample_sheet['date'] = pd.to_datetime(sample_sheet['input_path'].str.extract(r'(\d{4}\.\d{2}\.\d{2})')[0], format='%Y.%m.%d')
    sample_sheet.dropna(subset=['date'], inplace=True)
    sample_sheet.sort_values(by=['patient_id', 'date'], inplace=True)
    sample_sheet['fixed_image_path'] = sample_sheet.groupby('patient_id')['input_path'].transform(lambda x: oldest_date_value(sample_sheet.loc[x.index]))
    sample_sheet.drop(columns=['date'], inplace=True)
    sample_sheet.sort_values(by=['patient_id'], inplace=True)
    return sample_sheet

def make_dirs(sample_sheet):
    output_subdirs = list(sample_sheet['output_path'].apply(os.path.dirname))
    output_subdirs = list(set(output_subdirs))
    for dir in output_subdirs:
        if not os.path.exists(dir):
            os.mkdir(dir)
            print(f'Created directory: "{dir}"')

def main(args):
    # Check that all files in output directory have a correspondence in the input directory
    input_files_stripped = [re.sub(r'\.\w+$', '', get_base_directory_and_file(file)) for file in list_files(args.input_dir)]
    output_files_stripped = [re.sub(r'\.\w+$', '', get_base_directory_and_file(file)) for file in list_files(args.output_dir)]

    if output_files_stripped:
        for file in output_files_stripped:
            if file not in input_files_stripped:
                print(f'Warning: output file "{file}": no correspondence found in input directory.')

    if os.path.exists(args.sample_sheet_path):
        sample_sheet = pd.read_csv(args.sample_sheet_path)
        # Check that all output files are in log
        output_files = list_files(args.output_dir) 
        if output_files:
            for element in output_files:
                if element not in list(sample_sheet['output_path']):
                    print(f'Warning: output file "{element}" not found in output files log.')

        # Check that all logged input files exist
        input_files = list_files(args.input_dir)
        for element in list(sample_sheet['input_path']):
            if element not in input_files:
                print(f'Warning: input file "{element}" not found in input directory.')
    
    sample_sheet = generate_sample_sheet(args.input_dir, args.output_dir, input_ext=args.input_ext, output_ext=args.output_ext)

    sample_sheet.to_csv(args.sample_sheet_path, index=False)

    make_dirs(sample_sheet)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process input and output directories.')
    parser.add_argument('--input-dir', type=str, required=True,
                        help='Path to directory containing input files.')
    parser.add_argument('--output-dir', type=str, required=True,
                        help='Path to directory where output images will be saved.')
    parser.add_argument('--logs-dir', type=str, required=True,
                        help='Path to directory where log files will be stored.')
    parser.add_argument('--backup-dir', type=str, required=True,
                        help='Path to directory where backup files will be saved.')
    parser.add_argument('--input-ext', type=str, default='.nd2',
                        help='Input files extension.')
    parser.add_argument('--output-ext', type=str, default='.ome.tiff',
                        help='Output files extension.')
    
    args = parser.parse_args()
    main(args)
