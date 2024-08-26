process generateCSV {
    output:
    path 'csvfile.csv'

    script:
    """
    echo "name,age,converted" > csvfile.csv
    echo "Ginger,75,True" >> csvfile.csv
    echo "Paul,38,False" >> csvfile.csv
    echo "Yellow,27,False" >> csvfile.csv
    """
}

process processLine {
    input:
    val row

    output:
    stdout

    script:
    """
    demo_script_4.py --line "${row}"
    """
}

workflow {
    // Step 1: Capture the path to the CSV file from the process
    generateCSV()
    csv_file_path = generateCSV.out

    // Step 2: Parse the CSV file using splitCsv
    parsed_lines = csv_file_path
        .splitCsv(header: true)
        .map { row ->
            return row
        }

    // Step 3: Pass the parsed rows to a subsequent process
    processLine(parsed_lines)
}