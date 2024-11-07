// Parse rows from csv file
def parse_csv(csv_file_path) {
    channel
        .fromPath(csv_file_path)
        .splitCsv(header: true)
        .map { row ->
            return [
                patient_id          : row.patient_id,           // Patient identifier
                cycle_id            : row.cycle_id,             // Staining cycle identifier
                fixed_image_path    : row.fixed_image_path,     // Path to fixed image used in registration
                input_path          : row.input_path,           // Input path for registration
                output_path         : row.output_path           // Output path for conversion
            ]
        }
}

// Function to define registration parameters
def get_diffeomorphic_registration_params() {
    return Channel.of(
        tuple(
            params.crops_dir,            // Directory for storing image crops
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