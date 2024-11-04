import sys
import csv
import os

def process_stats_file(stats_file):
    struct_names = []
    volumes = []

    # Extract the base name of the file
    base_name = os.path.basename(stats_file)

    # Determine the prefix based on the base name
    if base_name.startswith('lh'):
        prefix = 'lh_'
    elif base_name.startswith('rh'):
        prefix = 'rh_'
    else:
        prefix = ''

    print(f"Processing file: {stats_file} with prefix: {prefix}")

    with open(stats_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if not line.startswith('#') and not line.startswith(' ') and not line.startswith('\n'):
                parts = line.split()
                struct_name = prefix + parts[0] + "_mm3_freesurfer"  # Add prefix and suffix
                volume_mm3 = parts[3]  # Extract GrayVol
                struct_names.append(struct_name)
                volumes.append(volume_mm3)
                print(f"Processed struct_name: {struct_name}, volume: {volume_mm3}")

    return struct_names, volumes

def generate_csv(struct_names, volumes, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(struct_names)  # Header row with StructName
        csv_writer.writerow(volumes)  # Row with volume data

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    struct_names, volumes = process_stats_file(input_file)
    generate_csv(struct_names, volumes, output_file)

    print(f"Data has been extracted from {input_file} and written to {output_file}.")

if __name__ == "__main__":
    main()

