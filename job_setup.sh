#!/bin/sh
#PBS -q nocg_workq
#PBS -N image_registration_pipeline
#PBS -S /bin/sh
#PBS -M ieo7086@ieo.it
#PBS -m abe
#PBS -l mem=2g
#PBS -l ncpus=2

cd $PBS_O_WORKDIR

source ~/.bashrc

cd /hpcnfs/scratch/DIMA/chiodin/repositories/image_registration_pipeline

nextflow run main.nf \
    -with-tower \
    --work_dir /hpcnfs/techunits/imaging/work/ATTEND/achiodin/registered_images \
    --sample_sheet_path /hpcnfs/techunits/imaging/work/ATTEND/achiodin/registered_images/logs/io/sample_sheet_current.csv \
    --crop_width_x 6000 \
    --crop_width_y 6000 \
    --overlap_x 2500 \
    --overlap_y 2500 \
    --max_workers 15
