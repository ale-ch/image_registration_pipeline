#!/bin/bash

main_dir="/Users/alessiochiodin/Documents/Repositories/image_registration_pipeline"
cd "$main_dir"

# Path to your CSV file
csv_file="${main_dir}/nd2_to_ome_tiff/tests/df.csv"

# Set the delimiter to comma
IFS=','

# Read the CSV file line by line
while read -r a b
do
    echo "Column 1: $a"
    echo "Column 2: $b"
    echo "-------------------------"
done < "$csv_file"