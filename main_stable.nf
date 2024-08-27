#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    FUNCTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

def parse_csv(ch) {
    // Parse a CSV channel with headers, returning a map for each row.
    ch
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

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    PIPELINE WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include {update_io} from './modules/io_handler.nf'                     
include {convert_images} from './modules/local/image_conversion/main.nf' 
include {register_images} from './modules/local/image_registration/main.nf' 

workflow {
    // Create a channel for I/O parameters
    update_io_params = channel.of(
        tuple(params.input_dir_conv,        // Input directory for conversion
            params.output_dir_conv,         // Output directory for conversion
            params.input_dir_reg,           // Input directory for registration
            params.output_dir_reg,          // Output directory for registration
            params.backup_dir,              // Directory for backups
            params.logs_dir                 // Directory for logs
        )
    )

    // Run I/O handler to update paths and directories
    update_io(update_io_params)
    csv_file_path = update_io.out  // Retrieve the path to the updated CSV file

    // Parse the CSV file into structured data
    parsed_lines = parse_csv(csv_file_path)

    // Prepare conversion parameters from parsed CSV data
    params_conv_1 = parsed_lines.map { rowMap ->
        tuple(rowMap.converted, rowMap.input_path_conv, rowMap.output_path_conv)
    }

    // Prepare registration parameters from parsed CSV data
    params_reg_1 = parsed_lines.map { rowMap ->
        tuple(rowMap.converted, rowMap.input_path_reg, rowMap.output_path_reg, rowMap.fixed_image_path)
    }

    // Define additional conversion parameters from user-defined inputs
    params_conv_2 = Channel.of(
        tuple(
            params.tilex,                // Tile size in x-direction
            params.tiley,                // Tile size in y-direction
            params.pyramid_resolutions,  // Number of pyramid resolutions
            params.pyramid_scale         // Scale factor for pyramid
        )
    )

    // Define additional registration parameters from user-defined inputs
    params_reg_2 = Channel.of(
        tuple(
            params.mappings_dir,         // Directory for storing mappings
            params.registered_crops_dir, // Directory for storing registered crops
            params.crop_width_x,         // Crop width in x-direction
            params.crop_width_y,         // Crop width in y-direction
            params.overlap_x,            // Overlap in x-direction
            params.overlap_y,            // Overlap in y-direction
            params.overlap_factor,       // Overlap factor
            params.auto_overlap,         // Flag for automatic overlap calculation
            params.delete_checkpoints,   // Flag to delete intermediate checkpoints
            params.logs_dir              // Directory for storing logs
        )
    )

    // Combine parsed CSV data with additional conversion parameters
    input_conv = params_conv_1
        .combine(params_conv_2)

    // Combine parsed CSV data with additional registration parameters
    input_reg = params_reg_1
        .combine(params_reg_2)

    // Execute image conversion module with combined parameters
    convert_images(input_conv)
    
    // Execute image registration module with combined parameters
    register_images(input_reg)
}
