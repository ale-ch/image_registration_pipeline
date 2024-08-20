import os
import re
import pandas as pd
import argparse
import logging
import datetime
import utils.logging_config as logging_config

logging_config.setup_logging()

logger = logging.getLogger(__name__)

def check_colnames(colnames):
    errors = []

    # Extract the first three column names
    first_col = colnames[0]
    second_col = colnames[1]
    third_col = colnames[2]

    # Check if the first column contains "id"
    if "id" not in first_col.lower():
        error_msg = f"First column name '{first_col}' does not contain 'id'"
        logging.error(error_msg)
        errors.append(error_msg)
    
    # Check if the second column contains "input"
    if "input" not in second_col.lower():
        error_msg = f"Second column name '{second_col}' does not contain 'input'"
        logging.error(error_msg)
        errors.append(error_msg)
    
    # Check if the third column contains "output"
    if "output" not in third_col.lower():
        error_msg = f"Third column name '{third_col}' does not contain 'output'"
        logging.error(error_msg)
        errors.append(error_msg)
    
    if errors:
        print("Errors in column name definitions. Check logs for details.")

    
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

def generate_sample_sheet(input_dir:str, output_dir:str, input_ext:str, output_ext:str):
    """
    Generate a sample sheet with input and output paths.

    Args:
        input_dir (str): The directory containing input files.
        output_dir (str): The directory to store output files.
        input_ext (str): The extension of the input files.
        output_ext (str): The extension of the output files.
    Returns:
        pd.DataFrame: The generated sample sheet.
    """
    if not str.startswith(input_ext, '.'):
        logger.error(f'File extension {input_ext}: Invalid file extension.')
    if not str.startswith(input_ext, '.'):
        logger.error(f'File extension {output_ext}: Invalid file extension.')

    # Function to join dir_path with the filename
    def join_path(file_path):
        return os.path.join(output_dir, file_path)

    def remove_extension(filename):
        return re.sub(r'(\.\w+)+$', '', filename)
    
    input_paths = [path for path in list_files(input_dir) if path.endswith(input_ext)]
    patient_ids = [os.path.basename(path).split('_', 1)[0] for path in input_paths]
    sample_sheet = pd.DataFrame({'patient_id': patient_ids, 'input_path': input_paths})
    sample_sheet['base_dir'] = sample_sheet['input_path'].apply(get_base_directory_and_file)
    sample_sheet['output_path'] = sample_sheet['base_dir'].apply(join_path)
    sample_sheet['output_path'] = sample_sheet['output_path'].apply(remove_extension) + output_ext
    sample_sheet['processed'] = sample_sheet['output_path'].apply(lambda x: os.path.exists(x))
    sample_sheet['filename'] = sample_sheet['output_path'].apply(remove_extension).apply(os.path.basename)
    sample_sheet = sample_sheet.drop(columns=['base_dir'])
    logger.debug('Sample sheet generated successfully.')
    return sample_sheet

def make_dirs(sample_sheet):
    output_subdirs = list(sample_sheet[args.colnames[2]].apply(os.path.dirname))
    output_subdirs = list(set(output_subdirs))
    for dir in output_subdirs:
        if not os.path.exists(dir):
            os.mkdir(dir)
            logger.info(f'Created directory: "{dir}"')

def main(args):
    # Check columns for order and naming
    check_colnames(args.colnames)

    handler = logging.FileHandler(os.path.join(args.logs_dir, 'update_io.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    formatted_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(args.export_path)
    sample_sheet_backup_path = os.path.join(args.backup_dir, formatted_datetime + '_' + filename)
    
    # Check that all files in output directory have a correspondence in the input directory
    input_files = [path for path in list_files(args.input_dir) if path.endswith(args.input_ext)]
    output_files = [path for path in list_files(args.output_dir) if path.endswith(args.output_ext)]
    input_filenames = [re.sub(r'(\.\w+)+$', '', os.path.basename(file)) for file in input_files if input_files]
    output_filenames = [re.sub(r'(\.\w+)+$', '', os.path.basename(file)) for file in output_files if output_files]

    if output_filenames:
        for filename, file_path in zip(output_filenames, output_files):
            if filename not in input_filenames:
                logger.warning(f'Output file "{file_path}": no correspondence found in input directory.')

    if os.path.exists(args.export_path):
        sample_sheet = pd.read_csv(args.export_path)
        # Check that all output files are in log
        if output_files:
            for element in output_files:
                if element not in list(sample_sheet[args.colnames[2]]):
                    logger.warning(f'Output file "{element}" not found in output files log.')

        # Check that all logged input files exist
        input_files = list_files(args.input_dir)
        for element in list(sample_sheet[args.colnames[1]]):
            if element not in input_files:
                logger.warning(f'Input file "{element}" not found in input directory.')
    
    sample_sheet = generate_sample_sheet(args.input_dir, args.output_dir, args.input_ext, args.output_ext)

    if args.colnames:
        sample_sheet.columns = args.colnames

    sample_sheet.to_csv(args.export_path, index=False)
    logger.info(f'Sample sheet exported successfully to {args.export_path}')
    sample_sheet.to_csv(sample_sheet_backup_path, index=False)
    logger.info(f'Sample sheet backed up successfully to {args.export_path}')

    make_dirs(sample_sheet)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process input and output directories.')
    parser.add_argument('--input-dir', type=str, required=True,
                        help='Path to directory containing input files.')
    parser.add_argument('--output-dir', type=str, required=True,
                        help='Path to directory where output images will be saved.')
    parser.add_argument('--input-ext', type=str, default='.nd2',
                        help='Input files extension.')
    parser.add_argument('--output-ext', type=str, default='.ome.tiff',
                        help='Output files extension.')
    parser.add_argument('--logs-dir', type=str, required=True,
                        help='Path to directory where log files will be stored.')
    parser.add_argument('--backup-dir', type=str, required=True,
                        help='Path to directory where backup files will be saved.')
    parser.add_argument('--colnames', type=str, required=True, nargs='*',
                    help="""\
                    Column names for the sample sheet. 
                    
                    Required number of columns: 5
                    
                    Naming conventions:
                      - First column: Must contain the pattern 'id'.
                      - Second column: Must contain the pattern 'input'.
                      - Third column: Must contain the pattern 'output'.
                      - Fourth column: No specific pattern required, but a name that refers to the process being handled is recommended.
                      - Fifth column: Must contain the pattern 'filename'.

                    Please ensure that the provided column names match the expected patterns to avoid errors.
                    """)
    parser.add_argument('--export-path', type=str, required=True,
                        help='Path where to save the sample sheet.')
    
    
    args = parser.parse_args()
    main(args)