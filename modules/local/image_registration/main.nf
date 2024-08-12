process image_registration {
    cpus 5
    memory '10G'
    publishDir "${params.outdir}", mode: "copy"
    container "docker://tuoprofilo/toolname:versione"
    tag "registration"
    
    input:
        tuple val(patient), path(moving_image), path(fixed_image)
    output:
        tuple path("${fixed_image}"), path("corrected_${moving_image}") emit: ome
    script:
    """
        python correct.py -fixed ${fixed_image} --moving ${moving_image} --output "corrected_${moving_image}"
    """
}