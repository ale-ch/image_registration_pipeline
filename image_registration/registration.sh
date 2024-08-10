#!/bin/bash

# root_dir="/hpcnfs"
# root_dir="/Volumes"
# current_dir="${root_dir}/scratch/DIMA/chiodin/repositories/image_registration_pipeline"
# data_dir="${root_dir}/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/data"
current_dir="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline"
data_dir="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline/image_registration/data/"

cd "$current_dir"
export PYTHONPATH="${current_dir}/image_registration/src:$PYTHONPATH"

python "${current_dir}/shared/update_io.py" \
    --input-dir "${current_dir}/image_registration/data/input" \
    --output-dir "${current_dir}/image_registration/data/output" \
    --input-ext ".tiff" \
    --output-ext ".tiff" \
    --logs-dir "${current_dir}/image_registration/logs/io" \
    --backup-dir "${current_dir}/image_registration/logs/io/backups" \


python "${current_dir}/image_registration/src/register_images.py" \
    --sample-sheet-path "${current_dir}/image_registration/logs/io/sample_sheet.csv" \
    --mappings-dir "${data_dir}/mappings" \
    --registered-crops-dir "${data_dir}/registered_crops" \
    --crop-width-x 500 \
    --crop-width-y 500 \
    --overlap-x 250 \
    --overlap-y 250 \
    --overlap-factor 0.3 \
    --logs-dir "${current_dir}/image_registration/logs" \
    --auto-overlap \
    --delete-checkpoints \
    