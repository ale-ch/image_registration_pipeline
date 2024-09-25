// Parse rows from csv file
def parse_csv(csv_file_path) {
    channel
        .fromPath(csv_file_path)
        .splitCsv(header: true)
        .map { row ->
            return [
                patient_id          : row.patient_id,           // Patient identifier
                input_path_conv     : row.input_path_conv,      // Input path for conversion
                output_path_conv    : row.output_path_conv,     // Output path for conversion
                converted           : row.converted,            // Conversion status
                fixed_image_path    : row.fixed_image_path,     // Path to fixed image used in registration
                input_path_reg      : row.input_path_reg,       // Input path for registration
                output_path_reg_1   : row.output_path_reg_1,    // Output path for affine registration
                output_path_reg_2   : row.output_path_reg_2,    // Output path for elastic registration
                registered          : row.registered,           // Registration status
                fixed_image         : row.fixed_image           // Flag for fixed image
            ]
        }
}

// Function to define registration parameters
def get_diffeomorphic_registration_params() {
    return Channel.of(
        tuple(
            params.crops_dir,             // Directory for storing image crops
            params.mappings_dir,         // Directory for storing mappings
            params.registered_crops_dir, // Directory for storing registered crops
            params.crop_width_x,         // Crop width in x-direction
            params.crop_width_y,         // Crop width in y-direction
            params.overlap_x,            // Overlap in x-direction
            params.overlap_y,            // Overlap in y-direction
            params.max_workers,          // Max number of parallel jobs
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