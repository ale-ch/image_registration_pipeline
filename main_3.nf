#!/usr/bin/env nextflow

nextflow.enable.dsl=2

// Function to parse CSV and create a channel
def parse_csv(path) {
    Channel
        .fromPath(path)
        .splitCsv(sep: ',', header: true)
        .map { row ->
            def a = row.A?.trim() ? row.A.toInteger() : 0 // Trim and convert to integer, default to 0
            def b = row.B?.trim() ? row.B.toInteger() : 0 // Trim and convert to integer, default to 0
            def c = row.C?.trim() ? row.C.toBoolean() : false // Trim and convert to boolean, default to false
            // println "Parsed row: A=${a}, B=${b}, C=${c}" // Debugging statement
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
    echo "A: ${A + 1}"
    echo "B: ${B}"
    echo "C: ${C}"
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
    # Debugging: Output the individual values received
    echo "Received A: ${A}"
    echo "Received B: ${B + 1}"
    echo "Received C: ${C}"
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
