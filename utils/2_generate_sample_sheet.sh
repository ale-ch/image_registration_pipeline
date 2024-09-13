#!/bin/bash

echo "$(dirname "$0")"

# Navigate to the directory containing script1.py
cd "$(dirname "$0")/../utils/generate_sample_sheet"

# Set the PYTHONPATH to include the directory with script2.py
export PYTHONPATH="$(pwd)/../../utils"

# Function to display usage
print_required_args() {
    echo "Required:"
    echo "  --work-dir /path/to/dir      Main directory path"
}

print_optional_args() {
    echo "Optional:"
    echo "  --export-path /path/to/file  Path to export file (default: <work_dir>/logs/io/<filename>.csv)"
    echo "  --make-dirs true|false       Create directories if they don't exist (default: true)"
    echo "  --input-dir-conv /path       Input directory for conversion (default: <work_dir>/data/input/image_conversion)"
    echo "  --output-dir-conv /path      Output directory for conversion (default: <work_dir>/data/output/image_conversion)"
    echo "  --output-dir-reg /path       Output directory for registration (default: <work_dir>/data/output/image_registration)"
}

usage() {
    echo "Usage: $0 [options]"
    print_required_args
    print_optional_args
    exit 1
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --work-dir) work_dir="$2"; shift ;;
        --export-path) export_path="$2"; shift ;;
        --make-dirs) make_dirs="$2"; shift ;;
        --input-dir-conv) input_dir_conv="$2"; shift;;
        --output-dir-conv) output_dir_conv="$2"; shift;;
        --output-dir-reg) output_dir_reg="$2"; shift;;
        *) usage ;;
    esac
    shift
done

# Validate required parameters
if [ -z "$work_dir" ]; then
    echo "Error: --work-dir is required"
    usage
fi

# Check if work_dir exists
if [ ! -d "$work_dir" ]; then
    echo "Error: work_dir does not exist: $work_dir"
    exit 1
fi

if [ -z "${export_path}" ]; then
    export_path="${work_dir}/logs/io/sample_sheet_current.csv"
fi

input_dir="${work_dir}/data/input"
output_dir="${work_dir}/data/output"
logs_dir="${work_dir}/logs"
backup_dir="${logs_dir}/io/backups"
sample_sheet_dir="${logs_dir}/io/"

# Process directories
## Image conversion
if [ -z "${input_dir_conv}" ]; then
    input_dir_conv="${input_dir}/image_conversion"
fi

if [ -z "${output_dir_conv}" ]; then
    output_dir_conv="${output_dir}/image_conversion"
fi

## Image registration
input_dir_reg="${output_dir_conv}"
if [ -z "${output_dir_reg}" ]; then
    output_dir_reg="${output_dir}/image_registration"
fi
mappings_dir="${work_dir}/data/mappings"
registered_crops_dir="${work_dir}/data/registered_crops"

# Create sample sheet for image conversion
echo "Creating conv_sample_sheet.csv"
python bin/utils/generate_sample_sheet/update_io.py \
    --input-dir "${input_dir_conv}" \
    --output-dir "${output_dir_conv}" \
    --input-ext ".nd2" \
    --output-ext ".ome.tiff" \
    --logs-dir "${logs_dir}" \
    --backup-dir "${backup_dir}" \
    --colnames patient_id input_path_conv output_path_conv converted filename \
    --export-path "${logs_dir}/io/conv_sample_sheet.csv" \
    --make-dirs

# Assign the fixed image to each patient id
echo "Assigning fixed_image_path to conv_sample_sheet.csv"
python bin/utils/generate_sample_sheet/assign_fixed_image.py \
    --samp-sheet-path "${logs_dir}/io/conv_sample_sheet.csv" \
    --export-path "${logs_dir}/io/conv_sample_sheet.csv"

# Create sample sheet for image registration
echo "Creating reg_sample_sheet.csv"
python bin/utils/generate_sample_sheet/update_io.py \
    --input-dir "${input_dir_conv}" \
    --output-dir "${output_dir_reg}" \
    --input-ext ".nd2" \
    --output-ext ".ome.tiff" \
    --logs-dir "${logs_dir}" \
    --backup-dir "${backup_dir}" \
    --colnames patient_id input_path_reg output_path_reg registered filename \
    --export-path "${logs_dir}/io/reg_sample_sheet.csv" \
    --make-dirs

python bin/utils/generate_sample_sheet/remove_columns.py \
    --csv-file-path "${logs_dir}/io/reg_sample_sheet.csv" \
    --column input_path_reg patient_id \
    --export-path "${logs_dir}/io/reg_sample_sheet.csv"

# Join I/O sheets
echo "Joining "${logs_dir}/io/conv_sample_sheet.csv" and "${logs_dir}/io/reg_sample_sheet.csv""
python bin/utils/generate_sample_sheet/join_samp_sheets.py \
    --samp-sheets-paths "${logs_dir}/io/conv_sample_sheet.csv" "${logs_dir}/io/reg_sample_sheet.csv" \
    --key-col-name "patient_id" \
    --filter-pending \
    --export-path "${export_path}" \
    --export-path-filtered "${export_path}" \
    --backup-dir "${logs_dir}/io/backups" 

python bin/utils/generate_sample_sheet/get_regular_crop_areas.py \
    --sample-sheet-path "${export_path}" \
    --ref-col 'input_path_conv' \
    --group-col 'patient_id' \
    --export-path "${export_path}" 
