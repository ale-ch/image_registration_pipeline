#!/usr/bin/env python

import argparse

def main(args):
    if args.converted == 'False':
        with open('out_conv_py.txt', 'a+') as f:
            f.write(args.input_path)
            f.write(args.output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--converted')
    parser.add_argument('--input-path')
    parser.add_argument('--output-path')
    args = parser.parse_args()
    main(args)