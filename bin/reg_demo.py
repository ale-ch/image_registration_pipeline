#!/usr/bin/env python

import argparse

def main(args):
    with open('out_reg_py.txt', 'a+') as f:
        f.write(str(args.input_path) + "\n")
        f.write(str(args.output_path) + "\n")
        f.write(str(args.fixed_image_path) + "\n")
        f.write(str(args.mappings_dir) + "\n")
        f.write(str(args.registered_crops_dir) + "\n")
        f.write(str(args.crop_width_x) + "\n")
        f.write(str(args.crop_width_y) + "\n")
        f.write(str(args.overlap_x) + "\n")
        f.write(str(args.overlap_y) + "\n")
        f.write(str(args.auto_overlap) + "\n")
        f.write(str(args.overlap_factor) + "\n")
        f.write(str(args.delete_checkpoints) + "\n")
        f.write(str(args.logs_dir) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to input images.')
    parser.add_argument('--output-path', type=str, required=True, 
                        help='Path to registered image.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to fixed image')
    parser.add_argument('--mappings-dir', type=str, required=True, 
                        help='Root directory to save mappings.')
    parser.add_argument('--registered-crops-dir', type=str, required=True, 
                        help='Root directory to save registered crops.')
    parser.add_argument('--crop-width-x', required=True, type=int, 
                        help='Crop width.')
    parser.add_argument('--crop-width-y', required=True, type=int, 
                        help='Crop height.')
    parser.add_argument('--overlap-x', type=int, 
                        help='Overlap of each crop along x axis.')
    parser.add_argument('--overlap-y', type=int, 
                        help='Overlap of each crop along y axis.')
    parser.add_argument('--auto-overlap', action='store_false', 
                        help='Automatically estimate overlap along both x and y axes.')
    parser.add_argument('--overlap-factor', type=float, 
                        help='Percentage by which the estimated overlap should be increased by.')
    parser.add_argument('--delete-checkpoints', action='store_false', 
                        help='Delete image mappings and registered crops files after processing.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to directory where log files will be stored.')
    args = parser.parse_args()
    
    main(args)