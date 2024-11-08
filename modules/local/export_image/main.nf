process export_image_1 {
    // cpus 5
    // memory "5G"
    cpus 20
    memory "100G"
    publishDir "${params.output_dir_reg}", mode: "copy"
    // container "docker://tuoprofilo/toolname:versione"
    tag "export_affine"

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
        val(output_path)

    script:
    """
    if [ "${input_path}" != "${fixed_image_path}" ]; then
        export_image.py \
            --input-path "${input_path}" \
            --output-dir "${params.output_dir_reg}" \
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
    // cpus 5
    // memory "5G"
    cpus 20
    memory "100G"
    publishDir "${params.output_dir_reg}", mode: "copy"
    // container "docker://tuoprofilo/toolname:versione"
    tag "export_diffeo"

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
        val(output_path)

    script:
    """
    if [ "${input_path}" != "${fixed_image_path}" ]; then
        export_image.py \
            --input-path "${input_path}" \
            --output-dir "${params.output_dir_reg}" \
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