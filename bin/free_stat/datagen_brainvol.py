import sys
import csv

def process_stats_file(input_file):
    data = {}
    with open(input_file, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if line.startswith('# Measure'):
            measure, abbreviation, description, volume, unit = line.strip().split(', ')
            measure = measure.split(' ')[-1] + "_mm3_freesurfer"  # Add suffix
            data[measure] = volume
    return data

def generate_csv(data, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    data = process_stats_file(input_file)
    generate_csv(data, output_file)
    
    print(f"Data has been extracted from {input_file} and written to {output_file}.")

if __name__ == "__main__":
    main()
