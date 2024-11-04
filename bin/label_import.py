import os
import csv
import re
import argparse

# Set up argparse
parser = argparse.ArgumentParser(description="Process filenames in the 'raw' folder and create a CSV file with IDs and age values.")
parser.add_argument('directory_path', type=str, help="Directory path where your 'raw' folder is located")
parser.add_argument('csv_file_path', type=str, help="Output CSV file path with filename and extension")
parser.add_argument('--age_value', type=str, default='-1', help="Age value to be assigned (default: -1)")

# Parse the arguments
args = parser.parse_args()

# Assign the parsed arguments to variables
directory_path = args.directory_path
csv_file_path = args.csv_file_path
age_value = args.age_value

# Get a list of filenames in the 'raw' folder
file_names = os.listdir(os.path.join(directory_path, 'raw'))

# Initialize an empty list to store rows
rows = []

# Regular expression pattern to match the filenames
pattern = re.compile(r'^sub-.*_ses-\d{2}_T1w-.*\.nii\.gz$')

# Process each filename and create rows for the CSV
for file_name in file_names:
    # Ignore files with the name ".DS_Store"
    if file_name == '.DS_Store':
        continue

    # Check if the filename matches the expected pattern
    if pattern.match(file_name):
        # Extract subject ID from the filename using split and remove '.nii.gz' extension
        subject_id = file_name[:-7]  # Remove the last 7 characters (.nii.gz)

        # Append a new row with ID and age values
        rows.append([subject_id, age_value])
    else:
        print(f"Warning: Unexpected filename format - '{file_name}'")

# Write the rows to the CSV file
with open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Write header
    csv_writer.writerow(['id', 'age'])
    
    # Write data rows
    csv_writer.writerows(rows)

print(f'CSV file "{csv_file_path}" created successfully.')
