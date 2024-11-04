import csv
import sys
import os

# Check if the correct number of arguments is provided
if len(sys.argv) != 3:
    print("Usage: python myscript.py input1 input2")
    sys.exit(1)

file1_path = sys.argv[1]
file2_path = sys.argv[2]

# Extract the parent directory name from file1_path
subject_id = os.path.basename(os.path.dirname(file1_path))

# Read the first CSV file
with open(file1_path, 'r') as file1:
    reader = csv.DictReader(file1)
    data1 = list(reader)

# Read the second CSV file
with open(file2_path, 'r') as file2:
    reader = csv.DictReader(file2)
    data2 = list(reader)

# Combine the data from both files
combined_data = []

# Append headers with the suffix "LST_AI"
combined_headers = [
    'Subject_ID',  # New column with suffix
    'Periventricular_lesions_LST_AI', 'Periventricular_volume_mm3_LST_AI',
    'Juxtacortical_lesions_LST_AI', 'Juxtacortical_volume_mm3_LST_AI',
    'Subcortical_lesions_LST_AI', 'Subcortical_volume_mm3_LST_AI',
    'Infratentorial_lesions_LST_AI', 'Infratentorial_volume_mm3_LST_AI',
    'Num_Lesions_LST_AI', 'Lesion_Volume_mm3_LST_AI'
]
combined_data.append(combined_headers)

# Extract data from the first file
data1_dict = {row['Region']: {'lesions': row['Num_Lesions'], 'volume': row['Lesion_Volume']} for row in data1}

# Extract data from the second file
data2_row = next(iter(data2))

# Construct combined row
combined_row = [
    subject_id,  # New column
    data1_dict['Periventricular']['lesions'], data1_dict['Periventricular']['volume'],
    data1_dict['Juxtacortical']['lesions'], data1_dict['Juxtacortical']['volume'],
    data1_dict['Subcortical']['lesions'], data1_dict['Subcortical']['volume'],
    data1_dict['Infratentorial']['lesions'], data1_dict['Infratentorial']['volume'],
    data2_row['Num_Lesions'], data2_row['Lesion_Volume']
]

# Append combined row to combined data
combined_data.append(combined_row)

# Write the combined data to a new CSV file
with open('combined.csv', 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerows(combined_data)

print("Combined CSV file has been created: 'combined.csv'")
