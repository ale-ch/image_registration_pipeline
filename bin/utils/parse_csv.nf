def parse_csv(csv_file_path) {
    channel
        .fromPath(csv_file_path)
        .splitCsv(header: true)
        .map { row ->
            return [
                patient_id      : row.patient_id,        // Patient identifier
                input_path_conv : row.input_path_conv,   // Input path for conversion
                output_path_conv: row.output_path_conv,  // Output path for conversion
                converted       : row.converted,         // Conversion status
                input_path_reg  : row.input_path_reg,    // Input path for registration
                output_path_reg : row.output_path_reg,   // Output path for registration
                registered      : row.registered,        // Registration status
                fixed_image_path: row.fixed_image_path   // Path to fixed image used in registration
            ]
        }
}
