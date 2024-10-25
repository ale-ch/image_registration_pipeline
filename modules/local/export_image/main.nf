process export_image {
    cpus 5
    memory "5G"
    // cpus 32
    // memory "170G"
    // errorStrategy 'retry'
    // maxRetries = 1
    // memory { 80.GB * task.attempt }
    publishDir "${params.output_dir_reg}", mode: "copy"
    // container "docker://tuoprofilo/toolname:versione"
    tag "export"

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
    # Extract the part after 'image_registration/'
    extracted_path=\$(echo "${input_path}" | sed 's|.*/image_registration/||')
    
    # Replace .nd2 with .h5
    affine_image_file="\${extracted_path%.nd2}.h5"
    
    # Construct path to affine registered image
    affine_image_path="${params.output_dir_reg}"/affine/"\$affine_image_file"
    
    # check if affine registered image exists
    if [ ! -f "\$affine_image_path" ]; then
        transformation='affine'
    else
        transformation='diffeomorphic'
    fi

    if [ "${input_path}" != "${fixed_image_path}" ]; then
        export_image.py \
            --input-path "${input_path}" \
            --output-dir "${params.output_dir_reg}" \
            --fixed-image-path "${fixed_image_path}" \
            --registered-crops-dir "${params.registered_crops_dir}" \
            --transformation "\$transformation" \
            --overlap-x "${params.overlap_x}" \
            --overlap-y "${params.overlap_y}" \
            --max-workers "${params.max_workers}" \
            --logs-dir "${params.logs_dir}"
    fi
    """
}