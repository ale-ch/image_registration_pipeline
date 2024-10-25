process stack_images {
    cpus 5
    memory "5G"
    // cpus 32
    // memory "170G"
    // errorStrategy 'retry'
    // maxRetries = 1
    // memory { 80.GB * task.attempt }
    publishDir "${params.output_dir_reg}", mode: "copy"
    // container "docker://tuoprofilo/toolname:versione"
    tag "stacking"
    
    input:
    tuple val(patient_id),
        val(fixed_image_path),
        val(input_path),
        val(output_path)

    output:
     tuple val(patient_id),
        val(fixed_image_path),
        val(input_path),
        val(output_path)
    
    script:
    """
    stack_images.py \
        --input-path "${output_path_reg_1}" \
        --output-path "${output_path_reg_2}" \
        --fixed-image-path "${fixed_image_path}" \
        --registered-crops-dir "${params.registered_crops_dir}" \
        --transformation "diffeomorphic" \
        --overlap-x "${params.overlap_x}" \
        --overlap-y "${params.overlap_y}" \
        --max-workers "${params.max_workers}" \
        --logs-dir "${params.logs_dir}" 
    """
}