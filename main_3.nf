#!/usr/bin/env nextflow

nextflow.enable.dsl=2

include {update_io} from './modules/io_handler.nf'
include {export_samples_to_process} from './modules/io_handler.nf'

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
    echo "A: ${A}"
    echo "B: ${B}"
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