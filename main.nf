#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    PIPELINE WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { parse_csv } from './bin/utils/workflow.nf'       
include { convert_to_h5 } from './modules/local/image_conversion/main.nf'               
include { convert_to_ome_tiff } from './modules/local/image_conversion/main.nf'
include { affine_registration } from './modules/local/image_registration/main.nf' 
include { diffeomorphic_registration } from './modules/local/image_registration/main.nf'
include { apply_mappings } from './modules/local/image_registration/main.nf'
include { export_image_1 } from './modules/local/export_image/main.nf'
include { export_image_2 } from './modules/local/export_image/main.nf'
include { stack_dapi_crops } from './modules/local/image_stacking/main.nf'
// include { stack_images } from './modules/local/image_stacking/main.nf'

workflow {

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        PARSE CSV INPUT
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */

    parsed_lines = parse_csv(params.sample_sheet_path)

    // Prepare conversion parameters from parsed CSV data
    params_parsed = parsed_lines.map { row ->
        tuple(
            row.patient_id,
            row.cycle_id,
            row.fixed_image_path,
            row.input_path,
            row.output_path
        )
    }

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        CONVERSION TO h5
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */

    convert_to_h5(params_parsed)

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        IMAGE REGISTRATION
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */

    affine_registration(convert_to_h5.out)
    export_image_1(affine_registration.out)
    // stack_dapi_crops(export_image_1.out) 
    // println stack_dapi_crops.out

    // crops_data = stack_dapi_crops.out
    //         .map { it ->
    //             def patient_id = it[0]
    //             def cycle_id = it[1]
    //             def fixed_image_path = it[2]
    //             def input_path = it[3]
    //             def output_path = it[4]
    //             def crops_paths = it[5]  // Paths to *.pkl files
    //             
    //             return crops_paths.collect { crops_path ->                    
    //                 return [patient_id, cycle_id, fixed_image_path, input_path, output_path, crops_path]
    //             }
    //         } 
    //         .flatMap { it }
    


    // def crops_data = []
    // stack_dapi_crops.out.each { it ->
    //     def fixed_image_path = it[2]
    //     def input_path = it[3]
    //     def output_path = it[4]
    //     def crops_paths = it[5]
// 
    //     def extract_patient_and_cycle = { path ->
    //         def filename = path.tokenize('/')[-1].tokenize('.')[0]
    //         def patient_id = filename.tokenize('_')[0]
    //         def cycle_id = filename.tokenize('_')[1..-1].join('_')
    //         return [patient_id, cycle_id]
    //     }
// 
    //     def fixed_info = extract_patient_and_cycle(fixed_image_path)
    //     def input_info = extract_patient_and_cycle(input_path)
// 
    //     if (fixed_info != input_info) { // Only process if fixed_info does not match input_info
    //         crops_paths.each { crops_path ->
    //             def crops_info = extract_patient_and_cycle(crops_path)
    //             def patient_id = crops_info[0]
    //             def cycle_id = crops_info[1]
// 
    //             def tuple = [
    //                 patient_id,
    //                 cycle_id,
    //                 fixed_info[0] == patient_id ? fixed_image_path : null,
    //                 input_info[0] == patient_id ? input_path : null,
    //                 output_path.tokenize('/')[-1].startsWith(patient_id) ? output_path : null,
    //                 crops_path
    //             ]
// 
    //             if (tuple[2] != null && tuple[3] != null && tuple[4] != null) {
    //                 results << tuple // Add tuple if all required paths are present
    //             }
    //         }
    //     }
    // }
    // crops_data // Return the final list of filtered tuples


    // diffeomorphic_registration(crops_data)
    // apply_mappings(diffeomorphic_registration.out)
    // export_image_2(apply_mappings.out)

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        IMAGE STACKING
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */

    // stack_images(export_image_2.out)

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        CONVERSION TO OME.TIFF
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */

    // input_conv = convert_to_ome_tiff(
    //     stack_images.out
    //         .combine(params_conv)
    // )
}
