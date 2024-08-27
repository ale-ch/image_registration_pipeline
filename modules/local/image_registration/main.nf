process register_images {
    cpus 5
    memory '10G'
    publishDir "${params.output_dir_reg}", mode: "copy"
    // container "docker://tuoprofilo/toolname:versione"
    tag "registration"
    
    input:
    tuple val(converted),
        val(input_path_reg),
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
        val(params.delete_checkpoints)

    script:
    """
    if [ "${converted}" == "True" ]; then
        echo "${converted}" > out_reg.txt
        echo "${input_path_reg}" >> out_reg.txt
        echo "${output_path_reg}" >> out_reg.txt
        echo "${fixed_image_path}" >> out_reg.txt
        echo "${params.mappings_dir}" >> out_reg.txt
        echo "${params.registered_crops_dir}" >> out_reg.txt
        echo "${params.crop_width_x}" >> out_reg.txt
        echo "${params.crop_width_y}" >> out_reg.txt
        echo "${params.overlap_x}" >> out_reg.txt
        echo "${params.overlap_y}" >> out_reg.txt
        echo "${params.overlap_factor}" >> out_reg.txt
        echo "${params.auto_overlap}" >> out_reg.txt
        echo "${params.delete_checkpoints}" >> out_reg.txt
    fi

    # register_images.py \
    #     --mappings-dir "${params.mappings_dir}" \
    #     --registered-crops-dir "${params.registered_crops_dir}" \
    #     --crop-width-x "${params.crop_width_x}" \
    #     --crop-width-y "${params.crop_width_y}" \
    #     --overlap-x "${params.overlap_x}" \
    #     --overlap-y "${params.overlap_y}" \
    #     --overlap-factor "${params.overlap_factor}" \
    #     --auto-overlap "${params.auto_overlap}" \
    #     --delete-checkpoints "${params.delete_checkpoints}"
    """
}