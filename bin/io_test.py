import pandas as pd
import argparse
import os

def main(args):
    a = ['hello', 'everybody', 'whopper']
    b = ['merry', '', 'big mac']
    c = [True, False, True]

    data = {'a': a, 'b': b, 'c': c}

    df = pd.DataFrame(data)
    
    df.to_csv(args.export_path)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process input and output directories.')
    parser.add_argument('--export-path', type=str, required=True,
                        help='Path where file will be saved.')
    
    args = parser.parse_args()
    main(args)