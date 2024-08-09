import pandas as pd
import argparse

def assign_fixed_image(input_path):
    def oldest_date_value(group):
        if not group.empty:
            return group.loc[group['date'].idxmin(), 'input_path']
        return None
    
    sample_sheet = pd.read_csv(input_path)

    sample_sheet['date'] = pd.to_datetime(sample_sheet['input_path'].str.extract(r'(\d{4}\.\d{2}\.\d{2})')[0], format='%Y.%m.%d')
    sample_sheet.dropna(subset=['date'], inplace=True)
    sample_sheet.sort_values(by=['patient_id', 'date'], inplace=True)
    sample_sheet['fixed_image_path'] = sample_sheet.groupby('patient_id')['input_path'].transform(lambda x: oldest_date_value(sample_sheet.loc[x.index]))
    sample_sheet.drop(columns=['date'], inplace=True)
    sample_sheet.sort_values(by=['patient_id'], inplace=True)
    return sample_sheet

def main(args):
    assign_fixed_image(args.sample_sheet_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assign the fixed image path for registration to each input-output image pair.")
    parser.add_argument('--input-path', type=str, required=True,
                        help='Path to sample sheet containing input-output pairs of paths to images.')
    parser.add_argument('--output-path', type=str, required=True,
                        help='Path where new sample sheet will be saved.')
    
    args = parser.parse_args()
    main(args)