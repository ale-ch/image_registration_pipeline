#!/usr/bin/env nextflow

nextflow.enable.dsl=2

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
    // Parse CSV file and create input Channel
    input = parse_csv(params.sample_sheet_path)

    // Process input for process 1 
    process_1_input = input
    .map { row -> 
            [
                input_path_conv: row.input_path_conv, 
                output_path_conv: row.output_path_conv, 
                converted: row.converted
            ] 
        }
    .filter { row -> !row.converted } // Filter where converted is false
    .map { row -> tuple(row.input_path_conv, row.output_path_conv, row.converted) }

    // Process input for process 2
    process_2_input = input
    .map { row -> 
            [
                input_path_reg: row.input_path_reg, 
                output_path_reg: row.output_path_reg, 
                converted: row.converted
            ] 
        }
    .filter { row -> row.converted } // Filter where converted is false
    .map { row -> tuple(row.input_path_reg, row.output_path_reg, row.converted) }

    // Pass inputs to processes
    process_1_result = process_1(process_1_input)
    process_2_result = process_2(process_2_input)

    // View results
    process_1_result.view()
    process_2_result.view()
}
