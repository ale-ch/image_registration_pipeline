#!/bin/bash

cd /hpcnfs/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline

python /hpcnfs/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/shared/update_paths.py \
    --input-root-path /hpcnfs/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/data \
    --output-root-path /hpcnfs/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/output/registered_stitched_images \
    --logs-dir /hpcnfs/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/develop/logs \
    --cur-logs-dir /hpcnfs/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/develop/logs/current \
    --backup-dir /hpcnfs/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/develop/logs/backups \
    --input-ext ".ome.tif" \
    --output-ext ".ome.tif" \
    --output-prefix REG_

python /hpcnfs/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/src/register_images.py \
    --cur-logs-dir /hpcnfs/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/develop/logs/current/ \
    --root-mappings-dir /hpcnfs/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/output/mappings \
    --root-registered_crops-dir /hpcnfs/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline/image_registration/output/registered_stitched_images \
    --fixed-image_pattern CYCLE_1 \
    --crop-width-x 500 \
    --crop-width-y 500 \
    --overlap-factor 0.3 \
    --delete-checkpoints True
