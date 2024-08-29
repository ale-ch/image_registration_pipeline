#!/bin/bash

# Function to print usage
usage() {
  echo "Usage: $0 --main_dir /path/to/main_dir"
  exit 1
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --main_dir)
      main_dir="$2"
      shift 2
      ;;
    *)
      echo "Unknown parameter passed: $1"
      usage
      ;;
  esac
done

# Check if main_dir is provided and valid
if [ -z "${main_dir}" ]; then
  echo "Error: --main_dir is required"
  usage
fi

if [ ! -d "${main_dir}" ]; then
  echo "Error: main_dir does not exist: ${main_dir}"
  exit 1
fi

# Define other directories based on main_dir
input_dir="${main_dir}/data/input"
output_dir="${main_dir}/data/output"
logs_dir="${main_dir}/logs"
backup_dir="${logs_dir}/io/backups"
sample_sheet_dir="${logs_dir}/io/"
sample_sheet_path="${main_dir}/logs/io/sample_sheet_current.csv"
input_dir_conv="${input_dir}/image_conversion"
output_dir_conv="${output_dir}/image_conversion"
input_dir_reg="${input_dir}/image_registration"
output_dir_reg="${output_dir}/image_registration"
mappings_dir="${main_dir}/data/mappings"
registered_crops_dir="${main_dir}/data/registered_crops"

# Create directories if they don't exist
mkdir -p "${input_dir}"
mkdir -p "${output_dir}"
mkdir -p "${logs_dir}"
mkdir -p "${backup_dir}"
mkdir -p "${sample_sheet_dir}"
mkdir -p "${input_dir_conv}"
mkdir -p "${output_dir_conv}"
mkdir -p "${input_dir_reg}"
mkdir -p "${output_dir_reg}"
mkdir -p "${mappings_dir}"
mkdir -p "${registered_crops_dir}"

echo "Directories have been created and verified. Proceeding with the pipeline."
