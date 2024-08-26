#!/usr/bin/env nextflow

nextflow.enable.dsl=2

// Define the first process to produce a CSV file using a Python script with pandas
process process1 {
    publishDir "${params.sample_sheet_dir}"

    input: 
    tuple val(something_1), val(something_2) 

    output:
    path 'output.csv'

    script:
    """
    io_test.py \
        --export-path "output.csv" \
        --something_1 "${something_1}" \
        --something_2 "${something_2}" 
    """
}

// Define the second process to add 7 to the Age field only when Crazy = True, using a Python script with pandas
process process2 {
    input:
    path csvFile

    script:
    """
    demo_script_2.py --csvFile "${csvFile}"
    """
}

// Define the second process to add 67 to the Age field only when Crazy = False, using a Python script with pandas
process process3 {
    input:
    path csvFile

    script:
    """
    demo_script_3.py --csvFile "${csvFile}"
    """
}

// Define the workflow
workflow {
    input_ch = channel
        .of(
            tuple('hello', 'world')
    )

    csvPath = process1(input_ch)
    process2(csvPath)
    process3(csvPath)
}
