#!/usr/bin/env nextflow

nextflow.enable.dsl=2

include {update_io} from './modules/io_handler.nf'

def parse_csv(path) {
    Channel
        .fromPath(path)
        .splitCsv(sep: ',', header: true)
        .map { row ->
            def id = row.patient_id != null ? row.patient_id.trim() : "null"
            def input_conv = row.input_path_conv != null ? row.input_path_conv.trim() : "null"
            def output_conv = row.output_path_conv != null ? row.output_path_conv.trim() : "null"
            def conv = row.converted != null ? (row.converted.trim().toBoolean() ?: false) : false
            def input_reg = row.input_path_reg != null ? row.input_path_reg.trim() : "null"
            def output_reg = row.output_path_reg != null ? row.output_path_reg.trim() : "null"
            def reg = row.registered != null ? (row.registered.trim().toBoolean() ?: false) : false
            def fixed_img = row.fixed_image_path != null ? row.fixed_image_path.trim() : "null"
                    
            return [
                patient_id: id, 
                input_path_conv: input_conv, 
                output_path_conv: output_conv, 
                converted: conv, 
                input_path_reg: input_reg, 
                output_path_reg: output_reg, 
                registered: reg, 
                fixed_image_path: fixed_img
            ]
        }
}

// Define the process_1 process (Bash script)
process process_1 {
    input:
    tuple val(input_path_conv), val(output_path_conv), val(converted)

    output:
    stdout

    script:
    """
    # Debugging: Output the values
    python /hpcnfs/scratch/DIMA/chiodin/repositories/image_registration_pipeline/bin/test_script_1.py \
        --A ${input_path_conv} \
        --B ${output_path_conv} \
        --C ${converted}
    """
}

// Define the process_2 process (Bash script)
process process_2 {
    input:
    tuple val(input_path_reg), val(output_path_reg), val(registered)

    output:
    stdout

    script:
    """
    # Debugging: Output the values
    python /hpcnfs/scratch/DIMA/chiodin/repositories/image_registration_pipeline/bin/test_script_2.py \
        --A ${input_path_reg} \
        --B ${output_path_reg} \
        --C ${registered}
    """
}

// Define the workflow
workflow {
    // Generate sample sheet
    update_io_input = channel.of(
        tuple(params.input_dir_conv, 
            params.output_dir_conv, 
            params.input_dir_reg, 
            params.output_dir_reg, 
            params.backup_dir, 
            params.logs_dir
        )
    )

    update_io_output = update_io(update_io_input)

    ////// GIVES ERROR: POSSIBLE SOLUTION: MAKE update_io OUTPUT SAMPLE SHEET PATH AS A CHANNEL //////
    // Parse CSV file and create input Channel
    input = update_io_output.flatMap {
        parse_csv(params.sample_sheet_path)
    }
    //////////////////////////////////////////////////////////////////////////////////////////////////////

    // Process input for process 1 
    process_1_input = input
    .filter { row -> !row.converted } 
    .map { row -> tuple(row.input_path_conv, row.output_path_conv, row.converted) }

    // Process input for process 2
    process_2_input = input
    .filter { row -> row.registered }
    .map { row -> tuple(row.input_path_reg, row.output_path_reg, row.registered) }

    // Pass inputs to processes
    process_1_result = process_1(process_1_input)
    process_2_result = process_2(process_2_input)

    // View results
    process_1_result.view()
    process_2_result.view()
}
