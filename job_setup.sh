#!/bin/sh
#PBS -S /bin/sh
#PBS -M ieo7086@ieo.it
#PBS -m abe
#PBS -l mem=1g
#PBS -l ncpus=2

cd $PBS_O_WORKDIR

source ~/.bashrc

cd /hpcnfs/scratch/DIMA/chiodin/repositories/image_registration_pipeline

nextflow run main.nf\
    -with-tower \
    --work_dir /hpcnfs/scratch/DIMA/chiodin/tests/img_reg_pipeline_3 \
    --sample_sheet_path /hpcnfs/techunits/imaging/work/ATTEND/achiodin/registered_images/logs/io/sampsheet_reg.csv \
    --crop_width_x \
    --crop_width_y \
    --overlap_x \
    --overlap_y
