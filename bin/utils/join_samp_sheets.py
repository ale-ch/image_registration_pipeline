#!/usr/bin/env python

import pandas as pd
import argparse
import datetime
import os
from functools import reduce

def main(args):
    # Create path to backup file
    filename = os.path.basename(args.export_path)
    formatted_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    sample_sheet_backup_path = os.path.join(args.backup_dir, formatted_datetime + '_' + filename)

    # Merge sample sheets
    samp_sheets = [pd.read_csv(path) for path in args.samp_sheets_paths]

    for idx, df in enumerate(samp_sheets):
        if idx > 0:
            samp_sheets[idx] = df.drop([df.columns[0]], axis=1)

    key = samp_sheets[0].columns[4]
    samp_sheets_joined = reduce(lambda left, right: pd.merge(left, right, on=key, how='left'), samp_sheets)
    samp_sheets_joined = samp_sheets_joined.drop(columns=key)

    # Export full sample sheet and backup to csv
    samp_sheets_joined.to_csv(args.export_path, index=False)
    samp_sheets_joined.to_csv(sample_sheet_backup_path, index=False)

    # Export filtered sample sheet
    if args.filter_pending:
        ref_colname = 'output_path_conv'
        samp_sheet_filtered = samp_sheets_joined[
            (
                (samp_sheets_joined['converted'] == False) | 
                (samp_sheets_joined['registered'] == False) | 
                (samp_sheets_joined['registered'] == '')
            )
        ]

        samp_sheet_filtered = samp_sheet_filtered.copy()
        samp_sheet_filtered['fixed_image'] = samp_sheet_filtered[ref_colname] == samp_sheet_filtered['fixed_image_path']

        samp_sheet_filtered.to_csv(args.export_path_filtered, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--samp-sheets-paths', type=str, required=True, nargs='*',
                        help='Paths to sample sheets.')
    parser.add_argument('--key-col-name', type=str, required=True, 
                        help='Name of primary key column to join the sample sheets by.')
    parser.add_argument('--filter-pending', action='store_true',
                        help='Filter the samples to be currently processed.')
    parser.add_argument('--export-path', type=str, required=True, 
                        help='Path where the full sample sheet will be saved.')
    parser.add_argument('--export-path-filtered', type=str, required=True, 
                        help='Path where the filtered sample sheet will be saved.')
    parser.add_argument('--backup-dir', type=str, required=True, 
                        help='Path to directory where sample sheet backups will be saved')
    args = parser.parse_args()
    main(args)