#!/usr/bin/env python

import argparse

def main(args):
    if args.converted == 'True':
        with open('out_reg_py.txt', 'a+') as f:
            f.write(args.input_path)
            f.write(args.output_path)
            f.write(args.fixed_img_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--converted')
    parser.add_argument('--input-path')
    parser.add_argument('--output-path')
    parser.add_argument('--fixed-img-path')
    args = parser.parse_args()
    main(args)