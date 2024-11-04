import os
import pandas as pd
import argparse

def merge_csv_files(directory, output_file):
    # Get a list of all CSV files in the directory
    csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]

    # Initialize an empty list to store dataframes
    dfs = []

    # Read each CSV file and append its contents to the list
    for file in csv_files:
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path)
        # Extract the study name
        study_name = os.path.splitext(os.path.basename(file))[0]  # Get the basename without extension
        # Insert the study name as the second column
        df.insert(1, 'StudyName', study_name)
        dfs.append(df)

    # Concatenate all dataframes in the list
    combined_df = pd.concat(dfs, ignore_index=True)

    # Save the combined dataframe to the specified output CSV file
    combined_df.to_csv(output_file, index=False)

    print(f"Data has been successfully combined and saved as {output_file}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Merge CSV files in a directory into a single CSV file")
    parser.add_argument("directory", help="Directory containing the CSV files")
    parser.add_argument("output_file", help="Output file name for the merged CSV data")
    args = parser.parse_args()

    # Call the function to merge CSV files
    merge_csv_files(args.directory, args.output_file)
