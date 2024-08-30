#!/usr/bin/env python

import pandas as pd
import argparse

def assign_fixed_image(input_path, input_col_name='output_path_conv'):
    def oldest_date_value(group):
        if not group.empty:
            return group.loc[group['date'].idxmin(), input_col_name]
        return None
    
    sample_sheet = pd.read_csv(input_path)
    pattern = r'(\d{4}\.\d{2}\.\d{2})'
    format = '%Y.%m.%d'
    sample_sheet['date'] = pd.to_datetime(sample_sheet[input_col_name].str.extract(pattern)[0], format=format)
    sample_sheet = sample_sheet.dropna(subset=['date'])
    sample_sheet['fixed_image_path'] = sample_sheet \
        .groupby('patient_id')[input_col_name] \
        .transform(lambda x: oldest_date_value(sample_sheet.loc[x.index]))
    sample_sheet = sample_sheet.drop(columns=['date'], axis=1)
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