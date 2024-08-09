#!/bin/bash

# root_dir="/hpcnfs"
# root_dir="/Volumes"
# 
# current_dir="${root_dir}/scratch/DIMA/chiodin/repositories/image_registration_pipeline"
# input_dir="${root_dir}/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/data"
# output_dir="${root_dir}/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/output"

current_dir="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline"
input_dir="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline/image_registration/data/input"
output_dir="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline/image_registration/data/output"

cd "$current_dir"

python "${current_dir}/shared/update_io.py" \
    --input-dir "${input_dir}" \
    --output-dir "${output_dir}" \
    --logs-dir "${current_dir}/image_registration/logs/io" \
    --backup-dir "${current_dir}/image_registration/logs/io/backups" \
    --input-ext ".nd2" \
    --output-ext ".nd2" \

# python "${current_dir}/image_registration/src/register_images.py" \
#     --sample-sheet-path "${current_dir}/image_registration/logs/io/sample_sheet.csv" \
#     --mappings-dir "${output_dir}/mappings" \
#     --registered-crops-dir "${output_dir}/registered_crops" \
#     --fixed-image-pattern CYCLE_1 \
#     --crop-width-x 500 \
#     --crop-width-y 500 \
#     --overlap-factor 0.3 \
#     --delete-checkpoints True \
#     --logs-dir "${current_dir}/image_registration/logs