#!/usr/bin/env nextflow

nextflow.enable.dsl=2

// Function to parse CSV and create a channel
def parse_csv(path) {
    Channel
        .fromPath(path)
        .splitCsv(sep: ',', header: true)
        .map { row ->
            return [row.A, row.B]
        }
}

// Define the AddOne process (Bash script)
process AddOne {
    input:
    tuple val(A), val(B)

    output:
    tuple val(A), val(B) 

    script:
    """
    # Debugging: Output the values
    echo "A: ${A}" > results.txt
    echo "B: ${B}" > results.txt
    """
}

// Define the AddTwo process (Bash script)
process AddTwo {
    input:
    tuple val(A), val(B)

    output:
    stdout

    script:
    script:
    """
    # Debugging: Output the individual values received
    echo "Received A: ${A + 1}"
    echo "Received A: ${B + 1}"
    """
}

// Define the workflow
workflow {
    input = parse_csv(params.sample_sheet_path)
    addOneResult = AddOne(input)
    addTwoResult = AddTwo(addOneResult)

    addOneResult.view()
    addTwoResult.view()
}