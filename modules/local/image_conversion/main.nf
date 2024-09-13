/*
    Convert nd2 files into multiple resolution hierarchical tiff files.
*/

process convert_fixed_images {
    memory "1G"
    cpus 1
    publishDir "${params.output_dir_conv}", mode: "copy"
    // container "docker://yinxiu/bftools:latest"
    tag "image_conversion"

    input:
    tuple val(converted), 
        val(registered),
        val(fixed_image),
        val(input_path_conv), 
        val(output_path_conv),
        val(output_path_reg),
        val(fixed_image_path),
        val(params.tilex),
        val(params.tiley),
        val(params.pyramid_resolutions),
        val(params.pyramid_scale)

    script:
    """
    if ([[ "${fixed_image}" == "True" || "${fixed_image}" == "TRUE" ]] && \
    [[ "${converted}" == "False" || "${converted}" == "FALSE" ]]); then 
    bfconvert -noflat -bigtiff \
        -tilex "${params.tilex}" \
        -tiley "${params.tiley}" \
        -pyramid-resolutions "${params.pyramid_resolutions}" \
        -pyramid-scale "${params.pyramid_scale}" \
        "${input_path_conv}" "${output_path_conv}"
    fi
    """
}

process convert_moving_images {
    memory "1G"
    cpus 1
    publishDir "${params.output_dir_conv}", mode: "copy"
    // container "docker://yinxiu/bftools:latest"
    tag "image_conversion"

    input:
    tuple val(converted), 
        val(registered),
        val(fixed_image),
        val(input_path_conv), 
        val(output_path_conv),
        val(output_path_reg),
        val(fixed_image_path),
        val(params.tilex),
        val(params.tiley),
        val(params.pyramid_resolutions),
        val(params.pyramid_scale)

    output:
    tuple val(fixed_image),
        val(output_path_conv),
        val(output_path_reg),
        val(fixed_image_path),

    script:
    """
    if ([[ "${fixed_image}" == "False" || "${fixed_image}" == "FALSE" ]] && \
    [[ "${converted}" == "False" || "${converted}" == "FALSE" ]]); then 
    bfconvert -noflat -bigtiff \
        -tilex "${params.tilex}" \
        -tiley "${params.tiley}" \
        -pyramid-resolutions "${params.pyramid_resolutions}" \
        -pyramid-scale "${params.pyramid_scale}" \
        "${input_path_conv}" "${output_path_conv}"
    fi
    """
}
