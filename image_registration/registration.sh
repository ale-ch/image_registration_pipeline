#!/bin/bash

current_dir="/Volumes/scratch/DIMA/chiodin/repositories/image_registration_pipeline"

cd "$current_dir"

python "${current_dir}/shared/update_paths.py" \
    --input-root-path "${current_dir}/image_registration/data" \
    --output-root-path "${current_dir}/image_registration/output/registered_stitched_images" \
    --logs-dir "${current_dir}/image_registration/logs" \
    --cur-logs-dir "${current_dir}/image_registration/logs/current" \
    --backup-dir "${current_dir}/image_registration/logs/backups" \
    --input-ext ".ome.tif" \
    --output-ext ".ome.tif" \
    --output-prefix REG_

python "${current_dir}/image_registration/src/register_images.py" \
    --cur-logs-dir "${current_dir}/image_registration/logs/current/" \
    --root-mappings-dir "${current_dir}/image_registration/output/mappings" \
    --root-registered-crops-dir "${current_dir}/image_registration/output/registered_crops" \
    --fixed-image-pattern CYCLE_1 \
    --crop-width-x 500 \
    --crop-width-y 500 \
    --overlap-factor 0.3 \
    --delete-checkpoints True
