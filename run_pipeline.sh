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


nextflow run main.nf \
    -with-tower \
    -resume \
    --work_dir /data/dimaimaging_dare/work/image_registration_pipeline \
    --sample_sheet_path /data/dimaimaging_dare/work/image_registration_pipeline/logs/io/sample_sheet_196056.csv \
    --crop_width_x 6000 \
    --crop_width_y 6000 \
    --overlap_x 2500 \
    --overlap_y 2500 \
    --max_workers 32

~                    
