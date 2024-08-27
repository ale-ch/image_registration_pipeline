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
        tuple path(input_path), path(output_path)
        int tilex from params.tilex
        int tiley from params.tiley
        int pyramid_resolutions from params.pyramid_resolutions
        int pyramid_scale from params.pyramid_scale

    output:
        stdout

    script:
    """
    echo "${input_path}" > out_conv.txt
    echo "${output_path}" >> out_conv.txt
    echo "${tilex}" > out_conv.txt
    echo "${tiley}" >> out_conv.txt
    echo "${pyramid_resolutions}" >> out_conv.txt
    echo "${pyramid_scale}" >> out_conv.txt

    # bfconvert \ 
    #     -noflat -bigtiff \ 
    #     -tilex "${tilex}" \ 
    #     -tiley "${tiley}" \ 
    #     -pyramid-resolutions "${pyramid_resolutions}" \ 
    #     -pyramid-scale "${pyramid_scale}" \ 
    #     "${input_path}" "${output_path}"
    """
}
