process stack_dapi_crops {
    cpus 2
    memory "80G"
    // cpus 32
    // memory "170G"
    // errorStrategy 'retry'
    // maxRetries = 1
    // memory { 80.GB * task.attempt }
    // publishDir "${params.output_dir_stack}", mode: "copy"
    // container "docker://tuoprofilo/toolname:versione"
    tag "crop_stacking"
    
    input:
    tuple val(patient_id),
        val(cycle_id),
        val(fixed_image_path),
        val(input_path),
        val(output_path)

    output:
     tuple val(patient_id),
        val(cycle_id),
        val(fixed_image_path),
        val(input_path),
        val(output_path),
        path("*pkl")
    
    script:
    """
    if [ "${input_path}" != "${fixed_image_path}" ]; then
        stack_dapi_crops.py \
                --input-path "${input_path}" \
                --output-dir "${params.output_dir_reg}" \
                --fixed-image-path "${fixed_image_path}" \
                --crops-dir-fixed "${params.crops_dir_fixed}" \
                --crops-dir-moving "${params.crops_dir_moving}" \
                --crop-width-x "${params.crop_width_x}" \
                --crop-width-y "${params.crop_width_y}" \
                --overlap-x "${params.overlap_x}" \
                --overlap-y "${params.overlap_y}" \
                --logs-dir "${params.logs_dir}" 
    fi
    """
}


process stack_images {
    cpus 20
    memory "100G"
    // cpus 32
    // memory "170G"
    // errorStrategy 'retry'
    // maxRetries = 1
    // memory { 80.GB * task.attempt }
    publishDir "${params.output_dir_stack}", mode: "copy"
    // container "docker://tuoprofilo/toolname:versione"
    tag "image_stacking"
    
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
        --output-dir "${params.output_dir_stack}" \
        --fixed-image-path "${fixed_image_path}" \
        --logs-dir "${params.logs_dir}" 
    """
}