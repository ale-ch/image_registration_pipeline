#!/bin/bash

# root_dir="/hpcnfs"
root_dir="/Volumes"

current_dir="${root_dir}/scratch/DIMA/chiodin/repositories/image_registration_pipeline"
input_dir="${root_dir}/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/data"
output_dir="${root_dir}/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/output"

cd "$current_dir"

python "${current_dir}/shared/update_paths.py" \
    --input-dir "${input_dir}" \
    --output-dir "${output_dir}/registered_stitched_images" \
    --logs-dir "${current_dir}/image_registration/logs/io" \
    --cur-logs-dir "${current_dir}/image_registration/logs/io/current" \
    --backup-dir "${current_dir}/image_registration/logs/backups" \
    --input-ext ".ome.tif" \
    --output-ext ".ome.tif" \
    --output-prefix REG_

python "${current_dir}/image_registration/src/register_images.py" \
    --cur-logs-dir "${current_dir}/image_registration/logs/io/current/" \
    --mappings-dir "${output_dir}/mappings" \
    --registered-crops-dir "${output_dir}/registered_crops" \
    --fixed-image-pattern CYCLE_1 \
    --crop-width-x 500 \
    --crop-width-y 500 \
    --overlap-factor 0.3 \
    --delete-checkpoints True
