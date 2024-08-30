#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    PIPELINE WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { parse_csv } from './bin/utils/workflow.nf'
include { get_registration_params } from './bin/utils/workflow.nf'     
include { get_conversion_params } from './bin/utils/workflow.nf'                        
include { convert_images } from './modules/local/image_conversion/main.nf' 
include { register_images } from './modules/local/image_registration/main.nf' 

workflow {

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        PARSE CSV INPUT
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */
    // Parse the CSV file into structured data
    parsed_lines = parse_csv(params.sample_sheet_path)

    // Prepare conversion parameters from parsed CSV data
    params_shared = parsed_lines.map { row ->
        tuple(
            row.converted,
            row.registered,
            row.fixed_image,
            row.input_path_conv, 
            row.output_path_conv, 
            row.input_path_reg, 
            row.output_path_reg, 
            row.fixed_image_path
        )
    }

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DEFINE PARAMETERS
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */
    // Conversion
    params_conv = get_conversion_params()
    
    // Registration
    params_reg = get_registration_params()
    
    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        IMAGE CONVERSION
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */
    // Combine parsed CSV data with additional conversion parameters
    input_conv = params_shared.combine(params_conv)

    // Execute image conversion module with combined parameters
    convert_images(input_conv)

    output_conv = convert_images.out

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        IMAGE REGISTRATION
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */

    // Combine converted image output with additional registration parameters
    input_reg = output_conv.combine(params_reg)
    
    // Execute image registration module with combined parameters
    register_images(input_reg)
}
