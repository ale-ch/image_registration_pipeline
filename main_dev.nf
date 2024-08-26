#!/usr/bin/env nextflow

nextflow.enable.dsl=2

include {update_io} from './modules/io_handler.nf'

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
