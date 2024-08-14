process update_io {
    input:
    path input_dir from params.input_dir
    path output_dir from params.output_dir
    path backup_dir from params.backup_dir
    path logs_dir from params.logs_dir

    script:
    """
    python bin/update_io.py \
        --input-dir "${input_dir}" \
        --output-dir "${output_dir}" \
        --backup-dir "${backup_dir}" \
        --input-ext "${params.input_ext}" \
        --output-ext "${params.output_ext}" \
        --logs-dir "${logs_dir}"
    """
}

process export_samples_to_process {
    input:
    path sample_sheet_path from params.sample_sheet_path
    path sample_sheet_current_path from params.sample_sheet_current_path
        
    script:
    """
    python bin/export_samples_to_process.py \
        --sample-sheet-path "${sample_sheet_path}" \
        --output-path "${sample_sheet_current_path}"
    """
}