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

process register_images {
    cpus 5
    memory '10G'
    publishDir "${params.outdir}", mode: "copy"
    container "docker://tuoprofilo/toolname:versione"
    tag "registration"
    
    input:
    path sample_sheet_current_path from params.sample_sheet_current_path
    path mappings_dir from params.mappings_dir
    path registered_crops_dir from params.registered_crops_dir
    int crop_width_x from params.crop_width_x
    int crop_width_y from params.crop_width_y
    int overlap_x from params.overlap_x
    int overlap_y from params.overlap_y
    float overlap_factor from params.overlap_factor
    boolean auto_overlap from params.auto_overlap
    boolean delete_checkpoints from params.delete_checkpoints

    script:
    """
    python bin/register_images.py \
        --sample-sheet "${sample_sheet_current_path}" \
        --mappings-dir "${mappings_dir}" \
        --registered-crops-dir "${registered_crops_dir}" \
        --crop-width-x ${crop_width_x} \
        --crop-width-y ${crop_width_y} \
        --overlap-x ${overlap_x} \
        --overlap-y ${overlap_y} \
        --overlap-factor ${overlap_factor} \
        --auto-overlap ${auto_overlap} \
        --delete-checkpoints ${delete_checkpoints}
    """
}

workflow {
    update_io()
    get_files_to_process()
    register_images()
}