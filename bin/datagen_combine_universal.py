import os
import pandas as pd
import argparse

def merge_csv_files(directory, output_file):
    # Define the filenames of the CSV files to be merged
    file1 = 'Fastsurfer_data.csv'
    file2 = 'Freesurfer_data.csv'

    # Construct the full file paths
    file1_path = os.path.join(directory, file1)
    file2_path = os.path.join(directory, file2)

    # Read the CSV files
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)

    # Print column names of both DataFrames
    print("Columns of Fastsurfer_data.csv:", df1.columns)
    print("Columns of Freesurfer_data.csv:", df2.columns)

    # Check if the necessary columns are present in both DataFrames
    if 'Subject_ID' not in df1.columns or 'Subject_ID' not in df2.columns:
        print("Error: 'Subject_ID' column not found in both DataFrames.")
        return
    if 'StudyName' not in df1.columns or 'StudyName' not in df2.columns:
        print("Error: 'StudyName' column not found in both DataFrames.")
        return

    # Merge the dataframes
    merged_df = pd.merge(df1, df2, on=['Subject_ID', 'StudyName'], how='outer', suffixes=('', '_from_Freesurfer'))

    # Save the merged dataframe to the specified output CSV file
    merged_df.to_csv(output_file, index=False)

    print(f"Data from {file1} and {file2} has been successfully merged and saved as {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge Fastsurfer and Freesurfer CSV files from a specified directory into a single output file.")
    parser.add_argument('directory', type=str, help='The directory containing the CSV files to merge')
    parser.add_argument('output_file', type=str, help='The name of the output file')

    args = parser.parse_args()

    # Call the function to merge CSV files
    merge_csv_files(args.directory, args.output_file)
