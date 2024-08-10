#!/bin/bash

# root_dir="/hpcnfs"
# root_dir="/Volumes"

# main_dir="${root_dir}/scratch/DIMA/chiodin/repositories/image_registration_pipeline"
# data_dir="${root_dir}/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/nd2_to_ome_tiff/data"

main_dir="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline"
data_dir="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline/nd2_to_ome_tiff/data/"

cd "$main_dir"
# export PYTHONPATH="${main_dir}/nd2_to_ome_tiff/src:$PYTHONPATH"

python "${main_dir}/shared/update_io.py" \
    --input-dir "${main_dir}/nd2_to_ome_tiff/data/input" \
    --output-dir "${main_dir}/nd2_to_ome_tiff/data/output" \
    --backup-dir "${main_dir}/nd2_to_ome_tiff/logs/io/backups" \
    --input-ext ".nd2" \
    --output-ext ".ome.tiff" \
    --logs-dir "${main_dir}/nd2_to_ome_tiff/logs/io" \


# RETURNS THE FILTERED SAMPLE SHEET WITH THE FILES TO BE PROCESSED
python "${main_dir}/shared/get_files_to_process.py" \
    --sample-sheet-path \
    --output-path

# Path to your CSV file
sample_sheet="${main_dir}/nd2_to_ome_tiff/logs/io/sample_sheet.csv"

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

done < "$sample_sheet"