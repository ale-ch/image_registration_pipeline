/*
Process to convert nd2 files into multiple resolution hierarchical tiff file.
*/

process update_io {
    input:
    path input_dir from params.input_dir
    path output_dir from params.output_dir
    path backup_dir from params.backup_dir
    path logs_dir from params.logs_dir
    val input_ext from params.input_ext
    val output_ext from params.output_ext

    script:
    """
    python bin/update_io.py \
        --input-dir "${input_dir}" \
        --output-dir "${output_dir}" \
        --backup-dir "${backup_dir}" \
        --input-ext "${input_ext}" \
        --output-ext "${output_ext}" \
        --logs-dir "${logs_dir}"
    """
}

process export_samples_to_process {
    // publishDir
    input:
    path sample_sheet_path from params.sample_sheet_path
    path sample_sheet_current_path from params.sample_sheet_current_path

    // output:
    // path("out*")
  
    script:
    """
    python bin/export_samples_to_process.py \
        --sample-sheet-path "${sample_sheet_path}" \
        --output-path "${sample_sheet_current_path}"
    """
}

process convert_images {
    memory "1G"
    cpus 1
    // publishDir "${params.output_dir}", mode: "copy"
    container "docker://yinxiu/bftools:latest"
    tag "image_conversion"

    input:
        tuple val(patient), path(input_path), path(output_path), val(fixed_imgs)
        int tilex from params.tilex
        int tilex from params.tiley
        int pyramid_resolutions from params.pyramid_resolutions
        int pyramid_scale from params.pyramid_scale

    output:
        tuple val(patient), path("*/${input_path.baseName}.ome.tiff"), val(fixed_imgs), emit: ome

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

workflow {
    update_io()
    export_samples_to_process()
    convert_images()
}
