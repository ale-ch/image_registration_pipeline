#!/usr/bin/env python

import pandas as pd
import argparse

def main(args):
    df = pd.read_csv(args.csvFile)

    # Add 7 to the Age column where Crazy is True
    df.loc[df["crazy"] == True, "age"] += 7

    df.to_csv("final_output_2.txt", index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--csvFile')
    args = parser.parse_args()
    main(args)