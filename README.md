[![Nextflow](https://img.shields.io/badge/nextflow%20DSL2-%E2%89%A522.10.1-23aa62.svg)](https://www.nextflow.io/)
[![Active Development](https://img.shields.io/badge/Maintenance%20Level-Actively%20Developed-brightgreen.svg)](https://gist.github.com/cheerfulstoic/d107229326a01ff0f333a1d3476e068d)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)

# .nd2 to .ome.tiff file conversion pipeline

## Contents
- [Contents](#contents)
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Input](#input)
- [Output](#output)

## Overview
This Nextflow pipeline converts ND2 files to OME.TIFF format. Users provide a CSV file specifying the paths to the ND2 files for conversion, and the pipeline outputs the converted files to a user-specified directory. This pipeline leverages Nextflow's capabilities to ensure efficient, scalable, and reproducible image file conversions.

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

The nextflow pipeline takes a csv samplesheet with 1 column as input

__IMPORTANT: HEADER is required__ 

| nd2file                     | 
| ---------------             | 
| absolute/path/to/file_1.nd2 |
| absolute/path/to/file_2.nd2 |
| .....                       | 

The absolute path to each file must be provided, __not__ the relative path.


## Output

The pipeline converts files specified in the input csv table from .nd2 to .ome.tiff, and stores the converted file in the provided output directory. 
