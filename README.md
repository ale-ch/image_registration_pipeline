[![Nextflow](https://img.shields.io/badge/nextflow%20DSL2-%E2%89%A522.10.1-23aa62.svg)](https://www.nextflow.io/)
[![Active Development](https://img.shields.io/badge/Maintenance%20Level-Actively%20Developed-brightgreen.svg)](https://gist.github.com/cheerfulstoic/d107229326a01ff0f333a1d3476e068d)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)

# Image registration pipeline

## Contents
- [Contents](#contents)
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Input](#input)
- [Output](#output)

## Overview
This Nextflow pipeline converts ND2 files to OME.TIFF format, and then registers the converted images with respect to the static images, based on user-specified parameters. Users provide the paths to the input and output directories for conversion and registration, and a set of specific parameters for each process. The pipeline automatically creates a CSV sample sheet containing the images to be processed, and then outputs the processed files to a user-specified output directory. This pipeline leverages Nextflow's capabilities to ensure efficient, scalable, and reproducible processing.

## Installation

Clone the repo

```
https://github.com/dimadatascience/nd2conversion.git
```


## Usage


To run the pipeline

```
nextflow run path_to/main.nf -profile singularity --input samplesheet.csv --outdir outdir
```

## Input




## Output

