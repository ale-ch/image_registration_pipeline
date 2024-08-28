#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    PIPELINE WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { parse_csv } from './bin/utils/parse_csv.nf'                   
include {convert_images} from './modules/local/image_conversion/main.nf' 
include {register_images} from './modules/local/image_registration/main.nf' 

/*
parse input
convert input
register input
*/

workflow {
    // Parse the CSV file into structured data
    parsed_lines = parse_csv(params.sample_sheet_path)

    // Prepare conversion parameters from parsed CSV data
    params_shared = parsed_lines.map { rowMap ->
        tuple(
            rowMap.input_path_conv, 
            rowMap.output_path_conv, 
            rowMap.input_path_reg, 
            rowMap.output_path_reg, 
            rowMap.fixed_image_path
        )
    }

    // Define additional conversion parameters from user-defined inputs
    params_conv = Channel.of(
        tuple(
            params.tilex,                // Tile size in x-direction
            params.tiley,                // Tile size in y-direction
            params.pyramid_resolutions,  // Number of pyramid resolutions
            params.pyramid_scale         // Scale factor for pyramid
        )
    )

    // Define additional registration parameters from user-defined inputs
    params_reg = Channel.of(
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
    input_conv = params_shared.concat(params_conv)

    // Execute image conversion module with combined parameters
    convert_images(input_conv)

    output_conv = convert_images.out
        .map { rowMap ->
            tuple(
                rowMap.input_path_reg, 
                rowMap.output_path_reg, 
                rowMap.fixed_image_path
            )
        }

    input_reg = output_conv.concat(params_reg)
    
    // Execute image registration module with combined parameters
    register_images(input_reg)
}
