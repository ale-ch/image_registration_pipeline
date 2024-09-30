import os
import argparse

def create_fake_nd2_files(input_dir, output_dir):
    """Traverse the input directory and create empty .nd2 files for each .ome.tiff file found."""
    # Walk through the input directory structure
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.ome.tiff'):
                # Get the relative path from input_dir
                relative_path = os.path.relpath(root, input_dir)
                
                # Create the corresponding .nd2 filename
                nd2_filename = file.replace('.ome.tiff', '.nd2')
                
                # Create the output path for the fake .nd2 file
                output_path = os.path.join(output_dir, relative_path, nd2_filename)
                
                # Ensure the directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Create the empty .nd2 file
                open(output_path, 'a').close()  # 'a' mode creates an empty file if it doesn't exist
                
                print(f"Created: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Create fake .nd2 files based on .ome.tiff files structure.")
    parser.add_argument('--input-dir', required=True, help="Directory containing the .ome.tiff files")
    parser.add_argument('--output-dir', default="fake_nd2", help="Output directory for the fake .nd2 files (default: fake_nd2)")
    
    args = parser.parse_args()
    
    # Create the fake .nd2 files
    create_fake_nd2_files(args.input_dir, args.output_dir)
    
if __name__ == "__main__":
    main()

