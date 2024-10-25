#!/usr/bin/env python

import argparse
import os
from utils.io_tools import load_nd2, save_h5
from utils.image_cropping import crop_2d_array

def convert_to_h5(src, dst, input_ext='.nd2'):
    if input_ext == '.nd2' or input_ext == 'nd2':
        data = load_nd2(src)

    ####### TEMPORARY ---- REMEMBER TO REMOVE ##########
    data = crop_2d_array(data, (0, 2000, 0, 2000))
    ####################################################

    save_h5(data, dst)

def main(args): 
    output_path = args.input_path.replace('.nd2', '.h5')

    if not os.path.exists(output_path):
        convert_to_h5(src=args.input_path, dst=output_path)

        if args.delete_src:
            os.remove(args.input_path)

if __name__ == '__main__':
    # Set up argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to the input (moving) image.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Directory to store log files.')
    parser.add_argument('--delete-src', action='store_true', 
                        help='Delete intermediate files after processing.')
    args = parser.parse_args()
    main(args)