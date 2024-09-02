#!/usr/bin/env python

import pandas as pd
import argparse

def assign_fixed_image(input_path, ref_colname='output_path_conv'):
    sample_sheet = pd.read_csv(input_path)

    # Extract date from the path
    sample_sheet['date'] = sample_sheet[ref_colname].str.extract(r'(\d{4}\.\d{2}\.\d{2})')

    # Convert the extracted date to datetime
    sample_sheet['date'] = pd.to_datetime(sample_sheet['date'], format='%Y.%m.%d')

    # Sort by patient_id and date
    sample_sheet = sample_sheet.sort_values(['patient_id', 'date'])

    # Group by patient_id and get the path corresponding to the oldest date
    sample_sheet['fixed_image_path'] = sample_sheet.groupby('patient_id')[ref_colname].transform('first')
    sample_sheet = sample_sheet.drop(columns=['date'])
    return sample_sheet

def main(args):
    samp_sheet = assign_fixed_image(args.samp_sheet_path)
    samp_sheet.to_csv(args.export_path, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assign the fixed image path for registration to each input-output image pair.")
    parser.add_argument('--samp-sheet-path', type=str, required=True,
                        help='Path to sample sheet containing input-output pairs of paths to images.')
    parser.add_argument('--export-path', type=str, required=True,
                        help='Path where new sample sheet will be saved.')
    
    args = parser.parse_args()
    main(args)