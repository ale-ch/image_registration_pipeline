#!/bin/bash

process_dir="image_registration"

# root_dir="/hpcnfs"
root_dir="/Volumes"

main_dir="${root_dir}/scratch/DIMA/chiodin/repositories/image_registration_pipeline"
# main_dir="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline"
data_dir="${main_dir}/${process_dir}/data"

cd "$main_dir"
export PYTHONPATH="${main_dir}/${process_dir}/src:$PYTHONPATH"

python "${main_dir}/shared/update_io.py" \
    --input-dir "${main_dir}/${process_dir}/data/input" \
    --output-dir "${main_dir}/${process_dir}/data/output" \
    --input-ext ".tiff" \
    --output-ext ".tiff" \
    --logs-dir "${main_dir}/${process_dir}/logs/io" \
    --backup-dir "${main_dir}/${process_dir}/logs/io/backups" \

# Returns sample sheet with the files to be currently processed
python "${main_dir}/shared/get_files_to_process.py" \
    --sample-sheet-path "${main_dir}/${process_dir}/logs/io/sample_sheet.csv" \
    --output-path "${main_dir}/${process_dir}/logs/io/sample_sheet_current.csv"

# python "${main_dir}/${process_dir}/src/register_images.py" \
python "${main_dir}/${process_dir}/tests/register_images_222.py" \
    --sample-sheet-path "${main_dir}/${process_dir}/logs/io/sample_sheet_current.csv" \
    --mappings-dir "${data_dir}/mappings" \
    --registered-crops-dir "${data_dir}/registered_crops" \
    --crop-width-x 500 \
    --crop-width-y 500 \
    --overlap-x 250 \
    --overlap-y 250 \
    --overlap-factor 0.3 \
    --logs-dir "${main_dir}/${process_dir}/logs" \
    --auto-overlap \
    --delete-checkpoints \
    