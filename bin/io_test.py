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
    df.to_csv(args.export_path, index=False)        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process input and output directories.')
    parser.add_argument('--export-path', type=str, required=True,
                        help='Path where file will be saved.')
    
    args = parser.parse_args()
    main(args)