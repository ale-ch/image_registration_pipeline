process export_image_1 {
    cpus 5
    memory "5G"
    // cpus 32
    // memory "170G"
    // errorStrategy 'retry'
    // maxRetries = 1
    // memory { 80.GB * task.attempt }
    publishDir "${params.output_dir_reg}", mode: "copy"
    // container "docker://tuoprofilo/toolname:versione"
    tag "export_1"
    
    input:
    tuple val(fixed_image),
        val(output_path_conv),
        val(output_path_reg_1),
        val(output_path_reg_2),
        val(fixed_image_path),
        val(params.crops_dir),
        val(params.mappings_dir),
        val(params.registered_crops_dir),
        val(params.crop_width_x),
        val(params.crop_width_y),
        val(params.overlap_x),
        val(params.overlap_y),
        val(params.max_workers),
        val(params.delete_checkpoints),
        val(params.logs_dir)

    output:
    tuple val(fixed_image),
        val(output_path_reg_1),
        val(output_path_reg_2),
        val(fixed_image_path),
        val(params.crops_dir),
        val(params.mappings_dir),
        val(params.registered_crops_dir),
        val(params.crop_width_x),
        val(params.crop_width_y),
        val(params.overlap_x),
        val(params.overlap_y),
        val(params.max_workers),
        val(params.delete_checkpoints),
        val(params.logs_dir)

    script:
    """
    if [ "${fixed_image}" == "False" ] || [ "${fixed_image}" == "FALSE" ]; then
        export_image.py \
            --input-path "${output_path_conv}" \
            --output-path "${output_path_reg_1}" \
            --fixed-image-path "${fixed_image_path}" \
            --registered-crops-dir "${params.registered_crops_dir}" \
            --transformation "affine" \
            --overlap-x "${params.overlap_x}" \
            --overlap-y "${params.overlap_y}" \
            --max-workers "${params.max_workers}" \
            --logs-dir "${params.logs_dir}" 
    fi
    """
}

process export_image_2 {
    cpus 5
    memory "5G"
    // cpus 32
    // memory "170G"
    // errorStrategy 'retry'
    // maxRetries = 1
    // memory { 80.GB * task.attempt }
    publishDir "${params.output_dir_reg}", mode: "copy"
    // container "docker://tuoprofilo/toolname:versione"
    tag "export_2"
    
    input:
    tuple val(fixed_image),
        val(output_path_reg_1),
        val(output_path_reg_2),
        val(fixed_image_path),
        val(params.registered_crops_dir),
        val(params.overlap_x),
        val(params.overlap_y),
        val(params.max_workers),
        val(params.delete_checkpoints),
        val(params.logs_dir)
    
    script:
    """
    if [ "${fixed_image}" == "False" ] || [ "${fixed_image}" == "FALSE" ]; then
        export_image.py \
            --input-path "${output_path_reg_1}" \
            --output-path "${output_path_reg_2}" \
            --fixed-image-path "${fixed_image_path}" \
            --registered-crops-dir "${params.registered_crops_dir}" \
            --transformation "diffeomorphic" \
            --overlap-x "${params.overlap_x}" \
            --overlap-y "${params.overlap_y}" \
            --max-workers "${params.max_workers}" \
            --logs-dir "${params.logs_dir}" 
    fi
    """
}