/*
Process to convert nd2 files into multiple resolution hierarchical tiff file.
*/

process convert_images {
    memory "1G"
    cpus 1
    // publishDir "${params.output_dir}", mode: "copy"
    container "docker://yinxiu/bftools:latest"
    tag "image_conversion"

    input:
        tuple val(patient), path(input_path_conv), path(output_path_conv)
        int tilex from params.tilex
        int tilex from params.tiley
        int pyramid_resolutions from params.pyramid_resolutions
        int pyramid_scale from params.pyramid_scale

    output:
        stdout

    script:
    """
        bfconvert \ 
            -noflat -bigtiff \ 
            -tilex ${tilex} \ 
            -tiley ${tiley} \ 
            -pyramid-resolutions ${pyramid_resolutions} \ 
            -pyramid-scale ${pyramid_scale} \ 
            ${input_path} ${output_path}
    """
}
