#!/usr/bin/env python

import pandas as pd
import argparse

def main(args):
    df = pd.read_csv(args.csv_file_path)

    if len(args.columns) == 1:
        df = df.drop(columns=[args.columns])
    else:
        df = df.drop(columns=args.columns)
    df.to_csv(args.export_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove column from dataframe')
    parser.add_argument('--csv-file-path', type=str, required=True,
                        help='Path to directory containing input files.')
    parser.add_argument('--columns', type=str, required=True, nargs='*',
                        help='Columns to remove.')
    parser.add_argument('--export-path', type=str, required=True,
                        help='Path to output file.')
    args = parser.parse_args()
    main(args)
