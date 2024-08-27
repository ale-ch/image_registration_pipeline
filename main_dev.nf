#!/usr/bin/env nextflow

nextflow.enable.dsl=2

include {update_io} from './modules/io_handler.nf'
include {convert_images} from './modules/local/image_conversion/main.nf'
include {register_images} from './modules/local/image_registration/main.nf'

workflow {
    update_io_params = channel.of(
        tuple(params.input_dir_conv, 
            params.output_dir_conv, 
            params.input_dir_reg, 
            params.output_dir_reg, 
            params.backup_dir, 
            params.logs_dir
        )
    )

    update_io(update_io_params)

    csv_file_path = update_io.out

    parsed_lines = csv_file_path
        .splitCsv(header: true)
        .map { row ->
            return [
                patient_id      : row.patient_id,
                input_path_conv : row.input_path_conv,
                output_path_conv: row.output_path_conv,
                converted       : row.converted,
                input_path_reg  : row.input_path_reg,
                output_path_reg : row.output_path_reg,
                registered      : row.registered,
                fixed_image_path: row.fixed_image_path
            ]
        }

    params_conv_1 = parsed_lines.map { rowMap ->
        tuple(rowMap.converted, rowMap.input_path_conv, rowMap.output_path_conv)
    }

    params_reg_1 = parsed_lines.map { rowMap ->
        tuple(rowMap.converted, rowMap.input_path_reg, rowMap.output_path_reg, rowMap.fixed_image_path)
    }

    params_conv_2 = Channel.of(
        tuple(
            params.tilex, 
            params.tiley, 
            params.pyramid_resolutions, 
            params.pyramid_scale
        )
    )

    params_reg_2 = Channel.of(
        tuple(
            params.mappings_dir,
            params.registered_crops_dir,
            params.crop_width_x,
            params.crop_width_y,
            params.overlap_x,
            params.overlap_y,
            params.overlap_factor,
            params.auto_overlap,
            params.delete_checkpoints
        )
    )

    input_conv = params_conv_1
        .combine(params_conv_2)

    input_reg = params_reg_1
        .combine(params_reg_2)

    convert_images(input_conv)
    register_images(input_reg)
}
