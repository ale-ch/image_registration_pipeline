#!/usr/bin/env nextflow

// Define the channel that will read the CSV file
def create_csv_channel(path) {
    Channel
        .fromPath(params.sample_sheet_path)
        .splitCsv(sep: ',', header: true)
        .map { row ->
            return [row.A, row.B]
        }
}

input = create_csv_channel(params.sample_sheet_path)

process process1 {
    input:
    tuple val(A), val(B)

    output:
    tuple val(A), val(B)

    script:
    """
    echo "A: ${A}, B: ${B}" > results.txt
    """
}

workflow {
    result = process1(input)
    result.view()
}
