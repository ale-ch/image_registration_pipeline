#!/usr/bin/env nextflow

nextflow.enable.dsl=2

// Function to parse CSV and create a channel
def parse_csv(csv_file_path) {
    return Channel.fromPath(csv_file_path)
        .splitCsv(header: true)
        .map { row -> 
            // Debugging: Print each row to see how it's being parsed
            println "Parsing Row: ${row}"

            // Ensure that row elements are correctly accessed
            def aValue = row['A'] as Integer
            def bValue = row['B'] as Integer

            // Return a map with the parsed values
            [A: aValue, B: bValue] 
        }
}

// Define the AddOne process (Bash script)
process AddOne {
    input:
    val row

    output:
    tuple val(row.A), val(row.B) // Output column A and B as a tuple

    script:
    """
    # Debugging: Output the entire row and individual values
    echo "Row: ${row}"
    echo "A: ${row.A}"
    echo "B: ${row.B}"
    """
}

// Define the AddTwo process (Bash script)
process AddTwo {
    input:
    tuple val(aValue), val(bValue) // Correctly receive column A and B

    output:
    stdout

    script:
    script:
    """
    # Debugging: Output the individual values received
    echo "Received aValue: ${aValue}"
    echo "Received bValue: ${bValue}"
    """
}

// Define the workflow
workflow {
    // Parse the CSV file and create a channel
    parsed_channel = parse_csv(params.sample_sheet_path)

    // Process data using AddOne and then trigger AddTwo
    addOneResult = parsed_channel | AddOne

    // Map the results from AddOne to AddTwo
    addTwoResult = addOneResult | AddTwo

    // Print final results
    addOneResult.view()
    addTwoResult.view()
}