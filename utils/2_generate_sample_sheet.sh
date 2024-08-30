#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 --main-dir /path/to/main_dir --export-path /path/to/file [--make-dirs <true/false>]" 
    exit 1
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --main-dir) main_dir="$2"; shift ;;
        --export-path) export_path="$2"; shift ;;
        --make-dirs) make_dirs="$2"; shift ;;
        *) usage ;;
    esac
    shift
done

# Validate required parameters
if [ -z "$main_dir" ]; then
    echo "Error: --main-dir is required"
    usage
fi

if [ -z "$export_path" ]; then
    echo "Error: --export-path is required"
    usage
fi

# Check if main_dir exists
if [ ! -d "$main_dir" ]; then
    echo "Error: main_dir does not exist: $main_dir"
    exit 1
fi

# Extract the directory path from export_path
export_dir=$(dirname "$export_path")

# Check if the export directory exists
if [ ! -d "$export_dir" ]; then
    echo "Error: The directory path for the export file does not exist: $export_dir"
    exit 1
fi

# main_dir='/hpcnfs/scratch/DIMA/chiodin/tests/img_reg_pipeline'
# export_path="${main_dir}/logs/io/sample_sheet_current.csv"

input_dir="${main_dir}/data/input"
output_dir="${main_dir}/data/output"
logs_dir="${main_dir}/logs"
backup_dir="${logs_dir}/io/backups"
sample_sheet_dir="${logs_dir}/io/"

# Process directories
## Image conversion
input_dir_conv="${input_dir}/image_conversion"
output_dir_conv="${output_dir}/image_conversion"

## Image registration
input_dir_reg="${output_dir_conv}"
# input_dir_reg="${input_dir}/image_registration"
output_dir_reg="${output_dir}/image_registration"
mappings_dir="${main_dir}/data/mappings"
registered_crops_dir="${main_dir}/data/registered_crops"

# Create new output folders and generate image conversion I/O sheet
python ./bin/utils/update_io.py \
    --input-dir "${input_dir_conv}" \
    --output-dir "${output_dir_conv}" \
    --input-ext ".nd2" \
    --output-ext ".tiff" \
    --logs-dir "${logs_dir}" \
    --backup-dir "${backup_dir}" \
    --colnames patient_id input_path_conv output_path_conv converted filename \
    --export-path "${logs_dir}/io/conv_sample_sheet.csv" \
    --make-dirs

# Create new output folders and generate image conversion I/O sheet
python ./bin/utils/update_io.py \
    --input-dir "${input_dir_reg}" \
    --output-dir "${output_dir_reg}" \
    --input-ext ".tiff" \
    --output-ext ".tiff" \
    --logs-dir "${logs_dir}" \
    --backup-dir "${backup_dir}" \
    --colnames patient_id input_path_reg output_path_reg registered filename \
    --export-path "${logs_dir}/io/reg_sample_sheet.csv" \
    --make-dirs

# python ./bin/utils/assign_fixed_image.py \
#     --samp-sheet-path "${logs_dir}/io/reg_sample_sheet.csv" \
#     --export-path "${logs_dir}/io/reg_sample_sheet.csv" 

python ./bin/utils/assign_fixed_image.py \
    --samp-sheet-path "${logs_dir}/io/conv_sample_sheet.csv" \
    --export-path "${logs_dir}/io/conv_sample_sheet.csv" 

# Join I/O sheets
python ./bin/utils/join_samp_sheets.py \
    --samp-sheets-paths "${logs_dir}/io/conv_sample_sheet.csv" "${logs_dir}/io/reg_sample_sheet.csv" \
    --key-col-name "patient_id" \
    --filter-pending \
    --export-path "${export_path}" \
    --export-path-filtered "${export_path}" \
    --backup-dir "${logs_dir}/io/backups" 