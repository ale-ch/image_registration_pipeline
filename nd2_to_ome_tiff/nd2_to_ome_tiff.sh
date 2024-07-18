#!/bin/bash

export PATH=$PATH:/hpcnfs/scratch/DIMA/chiodin/miniconda3/bin/

current_dir = "/hpcnfs/techunits/imaging/work/ATTEND/achiodin/image_registration_pipeline"
cd "$current_dir"

# Step 1: Define the input and output files
input_file="${current_dir}/nd2_to_ome_tiff/logs/current/cur_input_paths.txt"
output_file="${current_dir}/nd2_to_ome_tiff/logs/current/cur_output_paths.txt"

# Check if the input files already exist at the beginning of the script
if [[ -f $input_file ]]; then
  echo "Error: $input_file already exists!"
  exit 1
fi

if [[ -f $output_file ]]; then
  echo "Error: $output_file already exists!"
  exit 1
fi

# Step 2: Execute update_paths.py
python "${current_dir}/shared/update_paths.py"  \
                        --input-root_path /hpcnfs/techunits/imaging/PublicData/ImagingU/cborriero/nd2_images \
                        --output-root-path /hpcnfs/techunits/imaging/work/ATTEND/achiodin/ome_tiff_images \
                        --logs-dir "${current_dir}/nd2_to_ome_tiff/logs" \
                        --cur-logs-dir "${current_dir}/nd2_to_ome_tiff/logs/current" \
                        --backup-dir "/hpcnfs/data/P_DIMA_ATTEND/backups/nd2_to_ome_tiff/conversions_history" \
                        --input-ext ".nd2" \
                        --output-ext ".ome.tiff" \
                        --output-prefix ""

# Print out the paths from each file
echo "Input and Output Paths:"
while IFS= read -r input_path && IFS= read -r output_path <&3; do
  if [[ -n $input_path ]] && [[ -n $output_path ]]; then
    echo "Input Path: $input_path, Output Path: $output_path"

    bfconvert -noflat -bigtiff -tilex 512 -tiley 512 -pyramid-resolutions 3 -pyramid-scale 2 "$input_path" "$output_path"

    echo "Conversion of $input_path to $output_path completed successfully."
  else
    echo "Error: One of the files is empty or has no valid paths."
    exit 1
  fi
done < "$input_file" 3< "$output_file"

# Delete current input and output files 
rm "$input_file"
rm "$output_file"
