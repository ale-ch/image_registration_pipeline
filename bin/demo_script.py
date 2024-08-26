#!/usr/bin/env python

import argparse
import pandas as pd
from utils.df_from_line import df_from_line

def main(args):
    df = df_from_line(args.line)

    if 'converted' in df.columns:
        df['converted'] = df['converted'].map({'True': True, 'False': False})

    df['patient_id'] = pd.to_numeric(df['patient_id'])

    if not df["converted"].iloc[0]:  # Check the value of the "converted" column for the first row
        df["patient_id"] += 100

    df.to_csv('py_result.csv', index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--line')
    args = parser.parse_args()
    main(args)