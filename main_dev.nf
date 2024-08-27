#!/usr/bin/env nextflow

nextflow.enable.dsl=2

include {update_io} from './modules/io_handler.nf'
// include {convert_images} from './modules/local/image_conversion/main.nf'
// include {register_images} from './modules/local/image_registration/main.nf'

process process_1 {
    input:
    tuple val(converted), val(input_path_reg), val(output_path_reg), val(fixed_image_path)

    output:
    stdout

    script:
    """
    reg_demo.py \
        --converted "${converted}" \
        --input-path "${input_path_reg}" \
        --output-path "${output_path_reg}" \
        --fixed-img-path "${fixed_image_path}"
    """
}

process process_2 {
    input:
    tuple val(converted), val(input_path_conv), val(output_path_conv)

    output:
    stdout

    script:
    """
    # echo "${converted}" > out_conv.txt
    # echo "${input_path_conv}"  >> out_conv.txt
    # echo "${output_path_conv}" >> out_conv.txt

    conv_demo.py \
        --converted "${converted}" \
        --input-path "${input_path_conv}" \
        --output-path "${output_path_conv}"
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
            return [
                patient_id      : row.patient_id,
                input_path_conv : row.input_path_conv,
                output_path_conv: row.output_path_conv,
                converted       : row.converted,
                input_path_reg  : row.input_path_reg,
                output_path_reg : row.output_path_reg,
                registered      : row.registered,
                fixed_image_path: row.fixed_image_path
            ]
        }

    input_reg = parsed_lines.map { rowMap ->
        tuple(rowMap.converted, rowMap.input_path_reg, rowMap.output_path_reg, rowMap.fixed_image_path)
    }

    input_conv = parsed_lines.map { rowMap ->
        tuple(rowMap.converted, rowMap.input_path_conv, rowMap.output_path_conv)
    }

    process_1(input_reg)
    process_2(input_conv)
}
