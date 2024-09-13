// Parse rows from csv file
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
                fixed_image_path: row.fixed_image_path,  // Path to fixed image used in registration
                input_path_reg  : row.input_path_reg,    // Input path for registration
                output_path_reg : row.output_path_reg,   // Output path for registration
                registered      : row.registered,        // Registration status
                fixed_image     : row.fixed_image,        // Flag for fixed image
                start_row       : row.start_row,
                end_row         : row.end_row,
                start_col       : row.start_col,
                end_col         : row.end_col,
                start_row_fixed : row.start_row_fixed,
                end_row_fixed   : row.end_row_fixed,
                start_col_fixed : row.start_col_fixed,
                end_col_fixed   : row.end_col_fixed
            ]
        }
}

// Function to define registration parameters
def get_registration_params() {
    return Channel.of(
        tuple(
            params.mappings_dir,         // Directory for storing mappings
            params.registered_crops_dir, // Directory for storing registered crops
            params.crop_width_x,         // Crop width in x-direction
            params.crop_width_y,         // Crop width in y-direction
            params.overlap_x,            // Overlap in x-direction
            params.overlap_y,            // Overlap in y-direction
            params.max_workers,
            params.delete_checkpoints,   // Flag to delete intermediate checkpoints
            params.logs_dir              // Directory for storing logs
        )
    )
}

// Function to define conversion parameters
def get_conversion_params() {
    return Channel.of(
        tuple(
            params.tilex,                // Tile size in x-direction
            params.tiley,                // Tile size in y-direction
            params.pyramid_resolutions,  // Number of pyramid resolutions
            params.pyramid_scale         // Scale factor for pyramid
        )
    )
}