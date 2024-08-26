#!/usr/bin/env nextflow

nextflow.enable.dsl=2

process update_io {
    publishDir "${params.sample_sheet_dir}"

    input:
    tuple val(input_dir_conv),
        val(output_dir_conv),
        val(input_dir_reg),
        val(output_dir_reg),
        val(backup_dir),
        val(logs_dir)

    output:
    path 'sample_sheet_current.csv'

    script:
    """
    echo "${input_dir_conv}" > parsed_input.txt
    echo "${output_dir_conv}" >> parsed_input.txt
    echo "${input_dir_reg}" >> parsed_input.txt
    echo "${output_dir_reg}" >> parsed_input.txt
    echo "${backup_dir}" >> parsed_input.txt
    echo "${logs_dir}" >> parsed_input.txt

    echo "patient_id,input_path_conv,output_path_conv,converted,input_path_reg,output_path_reg,registered,fixed_image_path" > sample_sheet_current.csv
    echo "2,/hpcnfs/scratch/DIMA/chiodin/tests/img_reg_pipeline/image_conversion/data/input/2024.07.29_TREN/2_TREN.nd2,/hpcnfs/scratch/DIMA/chiodin/tests/img_reg_pipeline/image_conversion/data/output/2024.07.29_TREN/2_TREN.tiff,False,,,," >> sample_sheet_current.csv
    echo "1,/hpcnfs/scratch/DIMA/chiodin/tests/img_reg_pipeline/image_conversion/data/input/2024.07.29_TREN/1_TREN.nd2,/hpcnfs/scratch/DIMA/chiodin/tests/img_reg_pipeline/image_conversion/data/output/2024.07.29_TREN/1_TREN.tiff,True,/hpcnfs/scratch/DIMA/chiodin/tests/img_reg_pipeline/image_conversion/data/output/2024.07.29_TREN/1_TREN.tiff,/hpcnfs/scratch/DIMA/chiodin/tests/img_reg_pipeline/image_registration/data/output/2024.07.29_TREN/1_TREN.tiff,False,/hpcnfs/scratch/DIMA/chiodin/tests/img_reg_pipeline/image_conversion/data/output/2024.07.28_TRT/1_TRT.tiff" >> sample_sheet_current.csv
    echo "2,/hpcnfs/scratch/DIMA/chiodin/tests/img_reg_pipeline/image_conversion/data/input/2024.07.28_TRT/2_TRT.nd2,/hpcnfs/scratch/DIMA/chiodin/tests/img_reg_pipeline/image_conversion/data/output/2024.07.28_TRT/2_TRT.tiff,False,,,," >> sample_sheet_current.csv
    """
}

process process_1 {
    input:
    val row

    output:
    stdout

    script:
    """
    demo_script.py --line "${row}"
    """
}

workflow {
    update_io_params = channel.of(
        tuple(params.input_dir_conv, 
            params.output_dir_conv, 
            params.input_dir_reg, 
            params.output_dir_reg, 
            params.backup_dir, 
            params.logs_dir
        )
    )

    update_io(update_io_params)
    csv_file_path = update_io.out

    parsed_lines = csv_file_path
        .splitCsv(header: true)
        .map { row ->
            return row
        }

    parsed_lines.view()

    process_1(parsed_lines)
}