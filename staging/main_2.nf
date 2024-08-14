#!/usr/bin/env nextflow

nextflow.enable.dsl=2


/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    VALIDATE & PRINT PARAMETER SUMMARY
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

// Validate input parameters
WorkflowMain.initialise(workflow, params, log)

// Check input path parameters to see if they exist
def checkPathParamList = [ 
    params.input, params.database
    ]

for (param in checkPathParamList) { if (param) { file(param, checkIfExists: true) } }

include {image_conversion} from './modules/local/image_conversion/main.nf'
include {image_registration} from './modules/local/image_registration/main.nf'
/* include {conversion} from '/hpcnfs/scratch/DIMA/chiodin/repositories/nd2conversion/modules/local/image_conversion/main.nf' */

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    NAMED WORKFLOW FOR PIPELINE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

// Functions

// extract channels from input biomarkers sample sheet 
def extract_csv(csv_file) {
    // check that the sample sheet is not 1 line or less, because it'll skip all subsequent checks if so.
    file(csv_file).withReader('UTF-8') { reader ->
        def line, numberOfLinesInSampleSheet = 0;
        while ((line = reader.readLine()) != null) {
            numberOfLinesInSampleSheet++
            if (numberOfLinesInSampleSheet == 1){
                def requiredColumns = ["patient_id", "input_path", "output_path", "fixed_imgs"]
                def headerColumns = line
                if (!requiredColumns.every { headerColumns.contains(it) }) {
                    log.error "Header missing or CSV file does not contain all of the required columns in the header: ${requiredColumns}"
                    System.exit(1)
                }
            }
        }
        
        if (numberOfLinesInSampleSheet < 2) { // header only if one line
            log.error "Provided SampleSheet has less than two lines. Provide a samplesheet with header and at least a sample."
            System.exit(1)
        }
    }
 
    Channel.from(csv_file)
        .splitCsv(header: true)
        .map{ row ->
            return [row.patient_id, row.input_path, row.output_path]
            }
}

process update_io {
    input:
    path input_dir from params.input_dir
    path output_dir from params.output_dir
    path backup_dir from params.backup_dir
    path logs_dir from params.logs_dir
    val input_ext from params.input_ext
    val output_ext from params.output_ext

    script:
    """
    python bin/update_io.py \
        --input-dir "${input_dir}" \
        --output-dir "${output_dir}" \
        --backup-dir "${backup_dir}" \
        --input-ext "${input_ext}" \
        --output-ext "${output_ext}" \
        --logs-dir "${logs_dir}"
    """
}

process export_samples_to_process {
    // publishDir
    input:
    path sample_sheet_path from params.sample_sheet_path
    path sample_sheet_current_path from params.sample_sheet_current_path

    // output:
    // path("out*")
  
    script:
    """
    python bin/export_samples_to_process.py \
        --sample-sheet-path "${sample_sheet_path}" \
        --output-path "${sample_sheet_current_path}"
    """
}


workflow {exfile
    update_io()
    export_samples_to_process()

    input=extract_csv(file(params.input))

    conversion(input)

    paired_channel = conversion.out["ome"].groupTuple(by:0).map {
        patient_id, files, fixed_imgs ->

        for (int i = 0; i < fixed_imgs.size(); i++) {
            if(fixed_imgs[i] == 'true'){
                fix_image = files[i]
            }
        }
    
        collector = []
        for (int i = 0; i < fixed_imgs.size(); i++) {
            if(fixed_imgs[i] != 'true'){
                    collector << [patient_id, files[i], fix_image]
            }
        }
        
        return collector

    }.flatten().collate(3).view()
    image_registration(paired_channel)
}
