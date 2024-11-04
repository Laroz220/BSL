import os
import pandas as pd
import sys

def combine_csv_files(directory, output_location, output_file_name):
    # List of filenames to be combined
    file_names = [
        "lh_aparc_DKT_output.csv",
        "rh_aparc_DKT_output.csv",
        "brainvol_output.csv",
        "wmparc_output.csv",
        "aseg_output.csv"
    ]

    # Initialize an empty DataFrame to store combined data
    combined_data = None

    # Iterate through each file and read it into a DataFrame
    for file_name in file_names:
        file_path = os.path.join(directory, file_name)
        df = pd.read_csv(file_path)
        # If it's the first file, set the combined_data to the current DataFrame
        if combined_data is None:
            combined_data = df
        else:
            # Concatenate the current DataFrame horizontally to the combined_data
            combined_data = pd.concat([combined_data, df], axis=1)

    # Ensure that the output directory exists
    os.makedirs(output_location, exist_ok=True)

    # Write the combined data to a new CSV file
    combined_file_path = os.path.join(output_location, output_file_name)
    combined_data.to_csv(combined_file_path, index=False)

    print("Combined data has been saved to:", combined_file_path)

if __name__ == "__main__":
    # Check if correct number of arguments provided
    if len(sys.argv) != 4:
        print("Usage: python script.py <directory> <output_location> <output_file_name>")
        sys.exit(1)

    # Get directory, output location, and output file name from command line arguments
    directory = sys.argv[1]
    output_location = sys.argv[2]
    output_file_name = sys.argv[3]

    # Call the function to combine CSV files
    combine_csv_files(directory, output_location, output_file_name)

