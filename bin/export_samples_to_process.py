import pandas as pd
import argparse

def get_files_to_process(sample_sheet_path):
    full_sample_sheet = pd.read_csv(sample_sheet_path)
    filtered_sample_sheet = full_sample_sheet[full_sample_sheet['processed'] == False]
    return filtered_sample_sheet

def main(args):
    sample_sheet = get_files_to_process(args.sample_sheet_path)
    sample_sheet.to_csv(args.output_path, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample-sheet-path', type=str, required=True, 
                        help='Path to sample sheet.')
    parser.add_argument('--output-path', type=str, required=True, 
                        help='Path where the filtered sample sheet will be saved.')
    args = parser.parse_args()
    main(args)