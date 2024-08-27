#!/usr/bin/env python

import argparse
from utils.df_from_line import df_from_line

def main(args):
    df = df_from_line(args.line)

    if 'converted' in df.columns:
        df['converted'] = df['converted'].map({'True': True, 'False': False})

    if df["converted"].iloc[0]:  # Check the value of the "converted" column for the first row
        df.loc[:, ['input_path_reg', 'output_path_reg', 'fixed_image_path']].to_csv('out_reg.csv', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--converted')
    parser.add_argument('--input_path')
    parser.add_argument('--output_path')
    parser.add_argument('--fixed_img_path')
    args = parser.parse_args()
    main(args)