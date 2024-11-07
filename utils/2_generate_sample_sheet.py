import argparse
import os
import csv
import re
from collections import defaultdict
from datetime import datetime

def extract_date_from_path(path):
    """Extract the date from the input path using a regex pattern."""
    match = re.search(r'\d{4}\.\d{2}\.\d{2}', path)  # Matches dates like '2024.08.30'
    if match:
        return datetime.strptime(match.group(), '%Y.%m.%d')
    return None

def process_files(work_dir, input_dir=None, output_dir=None, output_csv="output.csv"):
    """Process files from input_dir and check existence in output_reg_2."""
    # Set default values for input_dir and output_dir if they are not provided
    if input_dir is None:
        input_dir = os.path.join(work_dir, 'data/input/image_registration')
    if output_dir is None:
        output_dir = os.path.join(work_dir, 'data/output/image_conversion/')

    patient_data = defaultdict(list)  # Dictionary to group files by patient_id
    
    # Step 1: Walk through the input directory and collect file information
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.nd2') or file.endswith('.h5'):  # Process .nd2 or .h5 files
                splitted_file = file.split('_')

                patient_id = splitted_file[0]
                cycle_id = f'{splitted_file[1]}_{splitted_file[2]}_{splitted_file[3]}'.split('.')[0]
                input_path = os.path.join(root, file)
                output_path = os.path.join(work_dir, 'data/output/image_conversion', f'{patient_id}.ome.tiff') 
                date = extract_date_from_path(input_path) 

                # Store data with date
                patient_data[patient_id].append({
                    'patient_id': patient_id,
                    'cycle_id': cycle_id,
                    'input_path': input_path,
                    'output_path': output_path,
                    'date': date  # Keep date in the dictionary for processing
                })

    # Step 2: Determine the fixed_image_path for each patient based on the least recent date
    rows = []
    for patient_id, data_list in patient_data.items():
        # Find the record with the least recent date
        least_recent = min(data_list, key=lambda x: x['date'])
        fixed_image_path = least_recent['input_path']

        # Assign the fixed_image_path to all records of the same patient_id
        for record in data_list:
            # Remove 'date' before appending to the rows
            del record['date']
            record['fixed_image_path'] = fixed_image_path
            # Set fixed_image to TRUE if output_path equals fixed_image_path
            rows.append(record)

    # Step 3: Write the results to a CSV file
    with open(output_csv, mode='w', newline='') as csvfile:
        fieldnames = ['patient_id', 'cycle_id', 'fixed_image_path', 'input_path','output_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)  # 'rows' now has no 'date' field
    
    print(f"CSV file '{output_csv}' generated successfully.")

def main():
    parser = argparse.ArgumentParser(description="Process input directory and generate CSV with file existence checks.")
    parser.add_argument('--work-dir', required=True, help="Directory structure for output (e.g., data/output/etc)")
    parser.add_argument('--input-dir', help="Directory containing the subdirectories with the files to be converted")
    parser.add_argument('--output-dir', help="Directory structure with the files to check for output_reg_2 and the 'registered' column")
    parser.add_argument('--output-csv', default="sample_sheet.csv", help="Name of the CSV output file (default: output.csv)")
    
    args = parser.parse_args()
    
    # Process the files and generate the CSV
    process_files(args.work_dir, args.input_dir, args.output_dir, args.output_csv)

if __name__ == "__main__":
    main()

