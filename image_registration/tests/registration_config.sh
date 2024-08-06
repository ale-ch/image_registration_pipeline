#!/bin/bash

# Read values from config.ini
# config_file="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline/image_registration/tests/config_local.ini"
# config_file="/Volumes/scratch/DIMA/chiodin/repositories/image_registration_pipeline/image_registration/configs/config_volumes.ini"
config_file="/hpcnfs/scratch/DIMA/chiodin/repositories/image_registration_pipeline/image_registration/configs/config_hpcnfs.ini"

get_config_value() {
    local section=$1
    local key=$2
    awk -F "=" -v section="$section" -v key="$key" '
    /^\[/{section_check=0} 
    /^\['"$section"'\]/{section_check=1} 
    section_check && $1 ~ key {gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2; exit}' $config_file
}

current_dir=$(get_config_value "Paths" "current_dir")
input_dir=$(get_config_value "Paths" "input_dir")
output_dir=$(get_config_value "Paths" "output_dir")

cd "$current_dir"

python "${current_dir}/shared/update_paths.py" \
    --input-dir "${input_dir}" \
    --output-dir "${output_dir}" \
    --logs-dir "$(get_config_value "UpdatePaths" "logs_dir")" \
    --cur-logs-dir "$(get_config_value "UpdatePaths" "cur_logs_dir")" \
    --backup-dir "$(get_config_value "UpdatePaths" "backup_dir")" \
    --input-ext "$(get_config_value "UpdatePaths" "input_ext")" \
    --output-ext "$(get_config_value "UpdatePaths" "output_ext")" \
    --output-prefix "$(get_config_value "UpdatePaths" "output_prefix")"

python "${current_dir}/image_registration/src/register_images.py" \
    --cur-logs-dir "$(get_config_value "RegisterImages" "cur_logs_dir")" \
    --mappings-dir "$(get_config_value "RegisterImages" "mappings_dir")" \
    --registered-crops-dir "$(get_config_value "RegisterImages" "registered_crops_dir")" \
    --fixed-image-pattern "$(get_config_value "RegisterImages" "fixed_image_pattern")" \
    --crop-width-x "$(get_config_value "RegisterImages" "crop_width_x")" \
    --crop-width-y "$(get_config_value "RegisterImages" "crop_width_y")" \
    --overlap-factor "$(get_config_value "RegisterImages" "overlap_factor")" \
    --delete-checkpoints "$(get_config_value "RegisterImages" "delete_checkpoints")"