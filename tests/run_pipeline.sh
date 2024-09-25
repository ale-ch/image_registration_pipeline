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


# nextflow run main.nf \
#     -with-tower \
#     --work_dir /hpcnfs/scratch/DIMA/chiodin/tests/test444 \
#     --sample_sheet_path /hpcnfs/scratch/DIMA/chiodin/tests/test444/logs/io/sampsheet1111.csv \
#     --overlap_x 500 \
#     --overlap_y 500 \
#     --crop_width_x 2500 \
#     --crop_width_y 2500


# nextflow run main.nf \
#     -with-tower \
#     --work_dir /hpcnfs/scratch/DIMA/chiodin/tests/test5 \
#     --sample_sheet_path /hpcnfs/scratch/DIMA/chiodin/tests/test5/logs/io/sampsheet_NEW.csv \
#     --overlap_x 2500 \
#     --overlap_y 2500 \
#     --crop_width_x 5000 \
#     --crop_width_y 5000


# nextflow run main.nf \
# 		 -with-tower \
# 		 --work_dir /hpcnfs/techunits/imaging/work/ATTEND/achiodin/registered_images \
# 		 --sample_sheet_path /hpcnfs/techunits/imaging/work/ATTEND/achiodin/registered_images/logs/io/sample_sheet_current.csv \
# 		 --crop_width_x 6000 \
# 		 --crop_width_y 6000 \
# 		 --overlap_x 2500 \
# 		 --overlap_y 2500 \
# 		 --max_workers 15 

		
nextflow run main.nf \
		 -with-tower \
		 --work_dir /hpcnfs/scratch/DIMA/chiodin/tests/images_h2000_w2000 \
		 --sample_sheet_path /hpcnfs/scratch/DIMA/chiodin/tests/images_h2000_w2000/logs/io/sample_sheet.csv \
		 --crop_width_x 600 \
		 --crop_width_y 600 \
		 --overlap_x 300 \
		 --overlap_y 300 \
		 --max_workers 2