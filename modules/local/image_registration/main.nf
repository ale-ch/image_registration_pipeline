/*
    Register images with respect to a predefined static image
*/

process register_images {
    cpus 10
    memory '20G'
    publishDir "${params.output_dir_reg}", mode: "copy"
    // container "docker://tuoprofilo/toolname:versione"
    tag "registration"
    
    input:
    tuple val(fixed_image),
        val(output_path_conv),
        val(output_path_reg),
        val(fixed_image_path),
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
        register_images.py \
            --input-path "${output_path_conv}" \
            --output-path "${output_path_reg}" \
            --fixed-image-path "${fixed_image_path}" \
            --mappings-dir "${params.mappings_dir}" \
            --registered-crops-dir "${params.registered_crops_dir}" \
            --crop-width-x "${params.crop_width_x}" \
            --crop-width-y "${params.crop_width_y}" \
            --overlap-x "${params.overlap_x}" \
            --overlap-y "${params.overlap_y}" \
            --max-workers ${params.max_workers} \
            --delete-checkpoints \
            --logs-dir "${params.logs_dir}"
    fi
    """
}