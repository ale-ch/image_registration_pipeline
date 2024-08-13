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

// Define processes that generates the CSV sample sheet

// Define the AddOne process (Bash script)
process AddOne {
    input:
    val row

    output:
    stdout

    script:
    """
    # Output the value of column A
    echo ${row.A}
    """
}

// Define the AddTwo process (Bash script)
process AddTwo {
    input:
    val row

    output:
    stdout

    script:
    """
    # Output the value of column B
    echo ${row.B}
    """
}

// Define the workflow
workflow {
    // Parse the CSV file and create a channel
    parsed_channel = parse_csv(params.sample_sheet_path)

    // Process data using AddOne and AddTwo processes
    addOneResult = parsed_channel | AddOne
    addTwoResult = parsed_channel | AddTwo

    // Print final results
    addOneResult.view()
    addTwoResult.view()
}