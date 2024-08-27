/*
Process to convert nd2 files into multiple resolution hierarchical tiff file.
*/

process convert_images {
    memory "1G"
    cpus 1
    publishDir "${params.output_dir_conv}", mode: "copy"
    // container "docker://yinxiu/bftools:latest"
    tag "image_conversion"

    input:
    tuple val(converted), 
        val(input_path_conv), 
        val(output_path_conv),
        val(params.tilex),
        val(params.tiley),
        val(params.pyramid_resolutions),
        val(params.pyramid_scale)

    output:
    stdout

    script:
    """
    if [ "${converted}" == "False" ]; then
        echo Converted: "${converted}" > out_conv.txt
        echo Input Path Conv: "${input_path_conv}" >> out_conv.txt
        echo Output Path Conv: "${output_path_conv}" >> out_conv.txt
        echo Tile X: "${params.tilex}" >> out_conv.txt
        echo Tile Y: "${params.tiley}" >> out_conv.txt
        echo Pyramid Resolutions: "${params.pyramid_resolutions}" >> out_conv.txt
        echo Pyramid Scale: "${params.pyramid_scale}" >> out_conv.txt
    fi

    # if [ "${converted}" == "False" ]; then
    #   bfconvert -noflat -bigtiff \
    #      -tilex "${params.tilex}" \
    #      -tiley "${params.tiley}" \
    #      -pyramid-resolutions "${params.pyramid_resolutions}" \
    #      -pyramid-scale "${params.pyramid_scale}" \
    #      "${input_path_conv}" "${output_path_conv}"
    # fi
    """
}
