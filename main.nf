#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    PIPELINE WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { parse_csv } from './bin/utils/workflow.nf'
include { get_elastic_registration_params } from './bin/utils/workflow.nf'     
include { get_conversion_params } from './bin/utils/workflow.nf'                        
include { convert_fixed_images } from './modules/local/image_conversion/main.nf'
include { convert_moving_images } from './modules/local/image_conversion/main.nf'  
include { affine_registration } from './modules/local/image_registration/main.nf' 
include { elastic_registration } from './modules/local/image_registration/main.nf'

workflow {

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        PARSE CSV INPUT
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */

    parsed_lines = parse_csv(params.sample_sheet_path)

    // Prepare conversion parameters from parsed CSV data
    params_shared = parsed_lines.map { row ->
        tuple(
            row.converted,
            row.registered,
            row.fixed_image,
            row.input_path_conv, 
            row.output_path_conv,  
            row.output_path_reg_1,
            row.output_path_reg_2, 
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
    params_reg = get_elastic_registration_params()
    
    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        IMAGE CONVERSION
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */

    // Combine parsed CSV data with additional conversion parameters
    input_conv = params_shared.combine(params_conv)

    convert_fixed_images(input_conv)
    convert_moving_images(input_conv)

    output_conv = convert_moving_images.out

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        IMAGE REGISTRATION
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */

    input_reg_1  = output_conv.combine(params_reg)
    affine_registration(input_reg_1)
    
    input_reg_2 = affine_registration.out
    elastic_registration(input_reg_2)
}
