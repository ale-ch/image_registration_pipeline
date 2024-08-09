#!/bin/bash

# root_dir="/hpcnfs"
# root_dir="/Volumes"
# 
# current_dir="${root_dir}/scratch/DIMA/chiodin/repositories/image_registration_pipeline"
# input_dir="${root_dir}/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/data"
# output_dir="${root_dir}/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/output"

current_dir="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline"
data_dir="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline/image_registration/data/"

cd "$current_dir"
export PYTHONPATH="${current_dir}/image_registration/src:$PYTHONPATH"

python "${current_dir}/shared/update_io.py" \
    --input-dir "${input_dir}" \
    --output-dir "${output_dir}" \
    --logs-dir "${current_dir}/image_registration/logs/io" \
    --backup-dir "${current_dir}/image_registration/logs/io/backups" \
    --input-ext ".png" \
    --output-ext ".png" \

python "${current_dir}/image_registration/tests/register_images_samplesheet.py" \
    --sample-sheet-path "${current_dir}/image_registration/logs/io/sample_sheet.csv" \
    --mappings-dir "${data_dir}/mappings" \
    --registered-crops-dir "${data_dir}/registered_crops" \
    --crop-width-x 300 \
    --crop-width-y 300 \
    --overlap-factor 0.3 \
    --delete-checkpoints False \
    --logs-dir "${current_dir}/image_registration/logs"