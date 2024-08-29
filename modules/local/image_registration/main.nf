/*
    Register images with respect to a predefined static image
*/

process register_images {
    // cpus 5
    // memory '10G'
    publishDir "${params.output_dir_reg}", mode: "copy"
    // container "docker://tuoprofilo/toolname:versione"
    tag "registration"
    
    input:
    tuple val(input_path_reg),
        val(output_path_reg),
        val(fixed_image_path),
        val(params.mappings_dir),
        val(params.registered_crops_dir),
        val(params.crop_width_x),
        val(params.crop_width_y),
        val(params.overlap_x),
        val(params.overlap_y),
        val(params.overlap_factor),
        val(params.auto_overlap),
        val(params.delete_checkpoints),
        val(params.logs_dir)

    script:
    """
    ###### SUBSTITUTE SCRIPT WITH register_images.py
    register_images.py \
        --input-path "${input_path_reg}" \
        --output-path "${output_path_reg}" \
        --fixed-image-path "${fixed_image_path}" \
        --mappings-dir "${params.mappings_dir}" \
        --registered-crops-dir "${params.registered_crops_dir}" \
        --crop-width-x "${params.crop_width_x}" \
        --crop-width-y "${params.crop_width_y}" \
        --overlap-x "${params.overlap_x}" \
        --overlap-y "${params.overlap_y}" \
        --auto-overlap \
        --delete-checkpoints \
        --overlap-factor "${params.overlap_factor}" \
        --logs-dir "${params.logs_dir}"
    """
}