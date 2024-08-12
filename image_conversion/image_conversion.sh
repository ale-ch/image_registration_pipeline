#!/bin/bash

process_dir="image_conversion"

# root_dir="/hpcnfs"
root_dir="/Volumes"

main_dir="${root_dir}/scratch/DIMA/chiodin/repositories/image_registration_pipeline"
# main_dir="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline"
data_dir="${main_dir}/${process_dir}/data"

cd "$main_dir"
# export PYTHONPATH="${main_dir}/${process_dir}/src:$PYTHONPATH"

python "${main_dir}/shared/update_io.py" \
    --input-dir "${main_dir}/${process_dir}/data/input" \
    --output-dir "${main_dir}/${process_dir}/data/output" \
    --backup-dir "${main_dir}/${process_dir}/logs/io/backups" \
    --input-ext ".nd2" \
    --output-ext ".ome.tiff" \
    --logs-dir "${main_dir}/${process_dir}/logs/io" \

# Returns sample sheet with the files to be currently processed
python "${main_dir}/shared/get_files_to_process.py" \
    --sample-sheet-path "${main_dir}/${process_dir}/logs/io/sample_sheet.csv" \
    --output-path "${main_dir}/${process_dir}/logs/io/sample_sheet_current.csv"

# Path to your CSV file
sample_sheet_current="${main_dir}/${process_dir}/logs/io/sample_sheet_current.csv"

# Set the delimiter to comma
IFS=','

# Read the CSV file line by line
while read -r patient_id input_path output_path processed
do
    echo "patient_id: $patient_id"
    echo "input_path: $input_path"
    echo "output_path: $output_path"
    echo "processed: $processed"
    echo "-------------------------"

    # bfconvert -noflat -bigtiff -tilex 512 -tiley 512 -pyramid-resolutions 3 -pyramid-scale 2 "$input_path" "$output_path"

done < "$sample_sheet_current"