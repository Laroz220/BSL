import os
import pandas as pd

def merge_csv_files(directory, output_file):
    # Get the list of CSV files in the directory
    csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]

    # Check if there are CSV files to merge
    if not csv_files:
        print("No CSV files found in the directory.")
        return

    # Initialize an empty DataFrame to store the merged data
    merged_df = pd.DataFrame()

    # Iterate over each CSV file and merge them
    for file in csv_files:
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path)
        merged_df = pd.concat([merged_df, df], ignore_index=True)

    # Save the merged dataframe to the specified output CSV file
    merged_df.to_csv(output_file, index=False)

    print(f"Data from all CSV files in the directory has been successfully merged and saved as {output_file}")

if __name__ == "__main__":
    # Specify the directory containing the CSV files (current working directory)
    directory = os.getcwd()

    # Specify the output file name
    output_file = 'Merged_Data.csv'

    # Call the function to merge CSV files
    merge_csv_files(directory, output_file)

