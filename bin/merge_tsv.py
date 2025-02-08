import pandas as pd
import argparse
import glob
import os

def merge_tsv_files(output_file):
    tsv_files = glob.glob("*.tsv")  # Get all TSV files in the current directory
    merged_df = pd.DataFrame()

    for file in tsv_files:
        try:
            df = pd.read_csv(file, sep='\t', usecols=["series_description", "is_derived"], dtype=str, on_bad_lines="skip")
            merged_df = pd.concat([merged_df, df], ignore_index=True)
        except Exception as e:
            print(f"Skipping {file} due to error: {e}")

    merged_df.drop_duplicates(inplace=True)  # Remove duplicates
    merged_df.to_csv(output_file, sep='\t', index=False)
    print(f"[INFO]: Merged TSV saved at {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge all .tsv files in the current directory, keeping only 'series_description' and 'is_derived' columns.")
    parser.add_argument("output_file", help="Path to save the merged .tsv file.")
    args = parser.parse_args()
    
    merge_tsv_files(args.output_file)
