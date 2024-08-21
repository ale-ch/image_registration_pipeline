#!/usr/bin/env nextflow

nextflow.enable.dsl=2

// Function to parse CSV and create a channel
def parse_csv(path) {
    Channel
        .fromPath(path)
        .splitCsv(sep: ',', header: true)
        .map { row ->
            def a = row.A?.trim() ? row.A.toInteger() : 0 
            def b = row.B?.trim() ? row.B.toInteger() : 0 
            def c = row.C?.trim() ? row.C.toBoolean() : false 
            println "Parsed row: A=${a}, B=${b}, C=${c}" 
            return [A: a, B: b, C: c]
        }
}

// Define the process_1 process (Bash script)
process process_1 {
    input:
    tuple val(A), val(B), val(C)

    output:
    tuple val(A), val(B), val(C)

    script:
    """
    # Debugging: Output the values
    python /hpcnfs/scratch/DIMA/chiodin/repositories/image_registration_pipeline/bin/test_script_1.py \
        --A ${A + 1} \
        --B ${B} \
        --C ${C}
    """
}

// Define the process_2 process (Bash script)
process process_2 {
    input:
    tuple val(A), val(B), val(C)

    output:
    stdout

    script:
    """
    # Debugging: Output the values
    python /hpcnfs/scratch/DIMA/chiodin/repositories/image_registration_pipeline/bin/test_script_2.py \
        --A ${A} \
        --B ${B + 1} \
        --C ${C}
    """
}

// Define the workflow
workflow {
    input = parse_csv(params.sample_sheet_path)

    // Split input based on the value of C
    process_1_input = input.filter { !it.C } // Only when C is false
    process_2_input = input.filter { it.C }  // Only when C is true

    // Execute process_1 only if C is false
    process_1_result = process_1(process_1_input)
    
    // Execute process_2 with the result of process_1 (if needed) or directly with filtered data
    process_2_result = process_2(process_2_input)

    // View results
    process_1_result.view()
    process_2_result.view()
}
