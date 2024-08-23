#!/usr/bin/env python

import argparse
import os 

def main(args):
    # path = '/Users/alessiochiodin/Documents/Programming/Tests/image_registration_pipeline/prints'
    path = '/hpcnfs/scratch/DIMA/chiodin/tests/img_reg_pipeline/prints'
    filename = 'test_script_2_output.txt'

    with open(os.path.join(path, filename), 'a+') as f:
        f.write(f"A: {args.A}")
        f.write('\n')
        f.write(f"B: {args.B}")
        f.write('\n')
        f.write(f"C: {args.C}")
        f.write('\n')
        f.write('\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--A')
    parser.add_argument('--B')
    parser.add_argument('--C')
    args = parser.parse_args()
    main(args)