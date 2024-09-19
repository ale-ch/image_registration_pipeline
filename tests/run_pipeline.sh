# nextflow run main.nf \
#     -with-tower \
#     --work_dir /hpcnfs/scratch/DIMA/chiodin/tests/test444 \
#     --sample_sheet_path /hpcnfs/scratch/DIMA/chiodin/tests/test444/logs/io/sample_sheet_current.csv \
#     --overlap_x 300 \
#     --overlap_y 300 \
#     --crop_width_x 1200 \
#     --crop_width_y 1200


# nextflow run main.nf \
#     -with-tower \
#     --work_dir /hpcnfs/scratch/DIMA/chiodin/tests/test444 \
#     --sample_sheet_path /hpcnfs/scratch/DIMA/chiodin/tests/test444/logs/io/sample_sheet_current.csv \
#     --overlap_x 500 \
#     --overlap_y 500 \
#     --crop_width_x 2500 \
#     --crop_width_y 2500


nextflow run main.nf \
    -with-tower \
    --work_dir /hpcnfs/scratch/DIMA/chiodin/tests/test444 \
    --sample_sheet_path /hpcnfs/scratch/DIMA/chiodin/tests/test444/logs/io/sampsheet1111.csv \
    --overlap_x 500 \
    --overlap_y 500 \
    --crop_width_x 2500 \
    --crop_width_y 2500