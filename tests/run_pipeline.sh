nextflow run main.nf \
    -with-tower \
    --work_dir /hpcnfs/scratch/DIMA/chiodin/tests/test444 \
    --sample_sheet_path /hpcnfs/scratch/DIMA/chiodin/tests/test444/logs/io/sample_sheet_current.csv \
    --overlap_x 200 \
    --overlap_y 200 \
    --crop_width_x 900 \
    --crop_width_y 900