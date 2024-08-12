/*
Process to convert nd2 files into multiple resolution hierarchical tiff file.
*/

process conversion{
    memory "1G"
    cpus 1
    publishDir "${params.outdir}", mode: "copy"
    container "docker://yinxiu/bftools:latest"
    tag "nd2conversion"
    
    input:
        tuple val(patient), path(input), val(fixed)
    output:
        tuple val(patient), path("*/${input.baseName}.ome.tiff"), val(fixed), emit: ome
    script:
    """
        folder=`realpath $input`
        folder=`dirname \$folder`
        folder=`basename \$folder`
        mkdir \$folder
        
        if [ ${params.database} != "null" ]; then
            if grep -qw $input appo  ; then 
                echo "Skipping $input" 
            else
                echo "$input" >> ${params.database}
                bfconvert -noflat -bigtiff -tilex 512 -tiley 512 -pyramid-resolutions 3 -pyramid-scale 2 $input \$folder/${input.baseName}.ome.tiff
                # touch \$folder/${input.baseName}.ome.tiff
            fi
        else
            bfconvert -noflat -bigtiff -tilex 512 -tiley 512 -pyramid-resolutions 3 -pyramid-scale 2 $input \$folder/${input.baseName}.ome.tiff
            # touch \$folder/${input.baseName}.ome.tiff
        fi
    """
}
