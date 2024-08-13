#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    VALIDATE & PRINT PARAMETER SUMMARY
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/


/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    NAMED WORKFLOW FOR PIPELINE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

// Functions
// extract channels from input biomarkers sample sheet 
def parse_csv(csv_file_path) {
    Channel.fromPath(csv_file_path)
        .splitCsv(header: true) // Assuming the CSV has a header
        .map { [A: it[0] as Integer, B: it[1] as Integer] }
}

// Include the addOne and addTwo processes from separate files
include {addOne} from './modules/local/test_processes/main.nf'
include {addTwo} from './modules/local/test_processes/main.nf'

// Define the GenerateCSV process
process GenerateCSV {
    output:
    path "${params.sample_sheet_path}" into csv_output

    script:
    """
    # Generate a CSV file with columns A and B
    echo 'A,B' > ${params.sample_sheet_path}
    
    # Use the parameters for range
    for i in \$(seq ${params.range_start} ${params.range_end}); do
        echo "\$i,\$((i * 2))" >> ${params.sample_sheet_path}
    done
    """
}

// Define the ProcessCSV process
process ProcessCSV {
    input:
    path csv_file from csv_output

    output:
    path csv_file into processed_csv_output

    script:
    """
    # Simply pass the file through
    cp ${csv_file} ${csv_file}
    """
}

// Define the input channel from the CSV file

// Define the workflow
workflow {
    // Invoke GenerateCSV process
    generate_csv_result = GenerateCSV()
    
    // Invoke ProcessCSV process and capture the output
    process_csv_result = ProcessCSV(generate_csv_result.out)

    input_channel = parse_csv(process_csv_result.out)

    // Send data to both processes
    input_channel.into { data ->
        data | addOne
        data | addTwo
    }

    // View the final results from AddTwo
    add_two_channel.view()
}
