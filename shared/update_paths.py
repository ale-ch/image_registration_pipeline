import os
import datetime
import shutil
import argparse

def get_directory_paths(root_path):
    """
    Retrieves paths of child directories under the given root path.

    Args:
        root_path (str): Root directory path.

    Returns:
        list: List of directory paths.
    """
    return [os.path.join(root_path, dir) for dir in os.listdir(root_path)]

def read_paths_from_file(file_path):
    """
    Reads paths from a text file and returns them as a list.

    Args:
        file_path (str): Path to the text file.

    Returns:
        list: List of paths read from the file.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return []

def write_paths_to_file(file_path, paths):
    """
    Writes a list of paths to a text file.

    Args:
        file_path (str): Path to the output text file.
        paths (list): List of paths to write to the file.

    Returns:
        None
    """
    with open(file_path, 'a') as file:  # Append mode to collect all paths
        for path in paths:
            file.write(path + '\n')

def create_empty_file(file_path):
    """
    Creates an empty file at the specified path.

    Args:
        file_path (str): Path to the file to be created.

    Returns:
        None
    """
    open(file_path, 'w').close()

def create_backup(file_path, backup_dir, base_filename):
    """
    Creates a backup copy of a file in the specified directory with a timestamped filename.

    Args:
        file_path (str): Path to the file to be backed up.
        backup_dir (str): Directory where the backup file will be saved.
        base_filename (str): Base filename for the backup file.

    Returns:
        None
    """
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    backup_filename = f"{base_filename}_{current_date}.txt"
    backup_path = os.path.join(backup_dir, backup_filename)
    shutil.copy(file_path, backup_path)

def get_output_pending_paths(output_paths_list, output_imgs_paths):
    """
    Compares two lists of paths and returns paths present in output_paths_list but not in output_imgs_paths.

    Args:
        output_paths_list (list): List of paths to check against.
        output_imgs_paths (list): List of paths to compare.

    Returns:
        list: List of paths present in output_paths_list but not in output_imgs_paths.
    """
    return [path for path in output_paths_list if path not in output_imgs_paths]

def get_input_pending_paths(paths, files_to_process):
    """
    Filters paths based on filenames present in the provided list of files to process.

    Args:
        paths (list): List of paths to filter.
        files_to_process (list): List of filenames to filter against.

    Returns:
        list: Filtered list of paths.
    """
    return [path for path in paths if os.path.basename(path) in files_to_process]

def get_files_with_extension(dir, extension):
    """
    Retrieves a list of files in a directory with a specified file extension.

    Args:
        dir (str): Directory path.
        extension (str): File extension to filter files.

    Returns:
        list: List of filenames with the specified extension.
    """
    return [file for file in os.listdir(dir) if file.endswith(extension)]

def remove_file_extension(filename):
    """
    Removes the file extension from a filename.

    Args:
        filename (str): Filename with extension.

    Returns:
        str: Filename without extension.
    """
    while True:
        filename, ext = os.path.splitext(filename)
        if not ext:
            break
    return filename

def main(args):
    # Get child directories paths
    input_imgs_dir_paths = get_directory_paths(args.input_root_path)
    output_imgs_dir_paths = get_directory_paths(args.output_root_path)
    print(input_imgs_dir_paths, output_imgs_dir_paths)

    # Read paths from files
    input_paths_list = read_paths_from_file(os.path.join(args.logs_dir, "input_paths.txt"))
    output_paths_list = read_paths_from_file(os.path.join(args.logs_dir, "output_paths.txt"))

    output_dir_paths_history_list = list(set(['/'.join(path.split('/')[:-1]) for path in output_paths_list]))

    # Check for nonexistent output directories
    nonexistent_paths = [path for path in output_dir_paths_history_list if path not in output_imgs_dir_paths]
    if nonexistent_paths:
        print("Warning: Missing directories:")
        for path in nonexistent_paths:
            print(f"  - {path}")

    # Initialize current process files
    cur_input_paths_file = os.path.join(args.cur_logs_dir, "cur_input_paths.txt")
    cur_output_paths_file = os.path.join(args.cur_logs_dir, "cur_output_paths.txt")
    create_empty_file(cur_input_paths_file)
    create_empty_file(cur_output_paths_file)

    # Populate lists of already processed images
    output_imgs_paths = [os.path.join(path, file) for path in output_imgs_dir_paths for file in os.listdir(path)]
    input_imgs_paths = [os.path.join(path, file) for path in input_imgs_dir_paths for file in os.listdir(path)]

    # Determine pending process paths
    output_pending_paths = get_output_pending_paths(output_paths_list, output_imgs_paths)
    files_to_process = [os.path.basename(path) for path in output_pending_paths]
    input_pending_paths = get_input_pending_paths(input_imgs_paths, files_to_process)

    # Write pending processs to current process files
    if input_pending_paths and output_pending_paths:
        write_paths_to_file(cur_input_paths_file, input_pending_paths)
        write_paths_to_file(cur_output_paths_file, output_pending_paths)

    # Update history files and create output directories
    new_input_paths = []
    new_output_paths = []

    for input_dir_path in input_imgs_dir_paths:
        target_files = get_files_with_extension(input_dir_path, args.input_ext)
        if not target_files:
            continue

        dir_name = os.path.basename(input_dir_path)
        output_dir_path_new = os.path.join(args.output_root_path, dir_name)
        
        if output_dir_path_new not in output_dir_paths_history_list and not os.path.exists(output_dir_path_new):
            os.mkdir(output_dir_path_new)

        for file in target_files:
            input_img_file_path = os.path.join(input_dir_path, file)
            file_no_ext = remove_file_extension(file)
            output_file = args.output_prefix + file_no_ext + args.output_ext
            output_img_file_path = os.path.join(output_dir_path_new, output_file)

            if input_img_file_path not in input_paths_list:
                new_input_paths.append(input_img_file_path)
                write_paths_to_file(cur_input_paths_file, [input_img_file_path])

            if output_img_file_path not in output_paths_list:
                new_output_paths.append(output_img_file_path)
                write_paths_to_file(cur_output_paths_file, [output_img_file_path])

    # Append new paths to the history files
    if new_input_paths:
        write_paths_to_file(os.path.join(args.logs_dir, "input_paths.txt"), new_input_paths)
    if new_output_paths:
        write_paths_to_file(os.path.join(args.logs_dir, "output_paths.txt"), new_output_paths)

    # Backup process history
    create_backup(os.path.join(args.logs_dir, "input_paths.txt"), args.backup_dir, "input_paths")
    create_backup(os.path.join(args.logs_dir, "output_paths.txt"), args.backup_dir, "output_paths")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process input and output directories.')
    parser.add_argument('--input-root-path', type=str, required=True,
                        help='Root directory path containing input images.')
    parser.add_argument('--output-root-path', type=str, required=True,
                        help='Root directory path where output images will be saved.')
    parser.add_argument('--logs-dir', type=str, required=True,
                        help='Directory path where log files will be stored.')
    parser.add_argument('--cur-logs-dir', type=str, required=True,
                        help='Directory path where current process log files will be stored.')
    parser.add_argument('--backup-dir', type=str, required=True,
                        help='Directory path where backup files will be saved.')
    parser.add_argument('--input-ext', type=str, default='.jpg',
                        help='File extension of input images.')
    parser.add_argument('--output-ext', type=str, default='.png',
                        help='File extension of output images.')
    parser.add_argument('--output-prefix', type=str, default='processed_',
                        help='Prefix to be added to output image filenames.')
    
    args = parser.parse_args()
    main(args)
