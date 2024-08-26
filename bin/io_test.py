#!/usr/bin/env python

import pandas as pd
import argparse

def main(args):
    data = {
    "name": ["Alice", "Bob"],
    "age": [30, 25],
    "city": ["New York", "Los Angeles"],
    "crazy": [True, False]
    }

    df = pd.DataFrame(data)

    df['test_1'] = args.something_1
    df['test_2'] = args.something_2
    df.to_csv(args.export_path, index=False)        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process input and output directories.')
    parser.add_argument('--export-path', type=str, required=True,
                        help='Path where file will be saved.')
    parser.add_argument('--something_1', type=str, required=True)
    parser.add_argument('--something_2', type=str, required=True)
    
    args = parser.parse_args()
    main(args)