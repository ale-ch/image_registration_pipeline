process update_io {
    input:
    path input_dir_conv from params.input_dir_conv
    path output_dir_conv from params.output_dir_conv
    path output_dir_reg from params.output_dir_reg
    path backup_dir from params.backup_dir
    path logs_dir from params.logs_dir

    script:
    """
    # Create new output folders and generate image conversion I/O sheet
    python "bin/update_io.py" \
        --input-dir ""${input_dir_conv}"" \
        --output-dir "${output_dir_conv}" \
        --input-ext ".nd2" \
        --output-ext ".tiff" \
        --logs-dir "${logs_dir}" \
        --backup-dir "${backup_dir}" \
        --colnames patient_id input_path_conv output_path_conv converted \
        --export-path "${logs_dir}/io/conv_sample_sheet.csv"

    # Create new output folders and generate image conversion I/O sheet
    python "bin/update_io.py" \
        --input-dir "${output_dir_conv}" \
        --output-dir "${output_dir_reg}" \
        --input-ext ".tiff" \
        --output-ext ".tiff" \
        --logs-dir "${logs_dir}" \
        --backup-dir "${backup_dir}" \
        --colnames patient_id input_path_reg output_path_reg registered \
        --export-path  "${logs_dir}/io/reg_sample_sheet.csv"

    python "utils/assign_fixed_image.py" \
        --samp-sheet-path "${logs_dir}/io/reg_sample_sheet.csv" \
        --export-path "${logs_dir}/io/reg_sample_sheet.csv" 

    # Join I/O sheets
    python "utils/join_samp_sheets.py" \
        --samp-sheets-paths "${logs_dir}/io/conv_sample_sheet.csv" "${logs_dir}/io/reg_sample_sheet.csv" \
        --key-col-name "patient_id" \
        --filter-pending \
        --export-path "${logs_dir}/io/sample_sheet_full.csv" \
        --export-path-filtered "${logs_dir}/io/sample_sheet_current.csv" \
        --backup-dir "${logs_dir}/io/backups" 
    """
}