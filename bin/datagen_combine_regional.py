import sys
import os
import pandas as pd

def combine_csv_files(directory, output_location, output_filename):
    # Check if the output file already exists
    if os.path.exists(os.path.join(output_location, output_filename)):
        # If it exists, load it to check existing subject IDs
        existing_data = pd.read_csv(os.path.join(output_location, output_filename))
        existing_subject_ids = set(existing_data['Subject_ID'].unique())
    else:
        existing_subject_ids = set()

    # Initialize an empty list to store DataFrames
    data_frames = []

    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            # Extract subject ID from the filename
            subject_id = os.path.splitext(filename)[0]

            # Check if subject ID already exists, if so, skip
            if subject_id in existing_subject_ids:
                print(f"Skipping subject ID {subject_id}, as it already exists.")
                continue
            
            # Read the CSV file
            file_path = os.path.join(directory, filename)
            data = pd.read_csv(file_path)
            
            # Add a new column for subject ID
            data.insert(0, 'Subject_ID', subject_id)
            
            # Append data to the list of DataFrames
            data_frames.append(data)

    # Concatenate all DataFrames in the list
    combined_data = pd.concat(data_frames, ignore_index=True)

    # Write the combined data to a new CSV file
    output_file_path = os.path.join(output_location, output_filename)
    combined_data.to_csv(output_file_path, index=False)

    print("Combined CSV file has been created successfully at:", output_file_path)


if __name__ == "__main__":
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 4:
        print("Usage: python script.py <directory> <output_location> <output_file_name>")
        sys.exit(1)

    # Extract command line arguments
    directory = sys.argv[1]
    output_location = sys.argv[2]
    output_filename = sys.argv[3]

    # Call the combine_csv_files function
    combine_csv_files(directory, output_location, output_filename)
