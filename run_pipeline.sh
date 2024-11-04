#!/bin/bash

#nextflow run main.nf \
#    -with-tower \
#    -resume \
#    --work_dir /data/dimaimaging_dare/work/image_registration_pipeline \
#    --sample_sheet_path /data/dimaimaging_dare/work/image_registration_pipeline/logs/io/sample_sheet.csv \
#    --crop_width_x 6000 \
#    --crop_width_y 6000 \
#    --overlap_x 2500 \
#    --overlap_y 2500 \
#    --max_workers 32


# nextflow run main.nf \
#     -with-tower \
#     -resume \
#     --work_dir /data/dimaimaging_dare/work/image_registration_pipeline \
#     --sample_sheet_path /data/dimaimaging_dare/work/image_registration_pipeline/logs/io/sample_sheet_196056.csv \
#     --crop_width_x 6000 \
#     --crop_width_y 6000 \
#     --overlap_x 2500 \
#     --overlap_y 2500 \
#     --max_workers 32

# nextflow run main.nf \
#     -with-tower \
#     --work_dir /hpcnfs/scratch/DIMA/chiodin/tests/images_h2000_w2000_b \
#     --sample_sheet_path  /hpcnfs/scratch/DIMA/chiodin/tests/images_h2000_w2000_b/logs/io/sample_sheet.csv \
#     --crop_width_x 1200 \
#     --crop_width_y 1200 \
#     --overlap_x 800 \
#     --overlap_y 800 \
#     --max_workers 1

#nextflow run main.nf \
#    -with-tower \
#    --work_dir /hpcnfs/scratch/DIMA/chiodin/tests/image_6k_6k \
#    --sample_sheet_path  /hpcnfs/scratch/DIMA/chiodin/tests/image_6k_6k/logs/io/sample_sheet.csv \
#    --crop_width_x 1200 \
#    --crop_width_y 1200 \
#    --overlap_x 800 \
#    --overlap_y 800 \
#    --max_workers 3
    
nextflow run main.nf \
    --with-tower \
    --work_dir /hpcnfs/scratch/DIMA/chiodin/tests/run_19S7 \
    --sample_sheet_path /hpcnfs/scratch/DIMA/chiodin/tests/run_19S7/logs/io/sample_sheet.csv \
    --crop_width_x 7000 \
    --crop_width_y 7000 \
    --overlap_x 3000 \
    --overlap_y 3000 \
    --max_workers 10       

  