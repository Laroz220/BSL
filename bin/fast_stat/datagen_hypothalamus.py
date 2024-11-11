import sys
import csv

def process_stats_file(input_file):
    data = {}
    with open(input_file, 'r') as file:
        lines = file.readlines()
    start_processing = False
    for line in lines:
        if line.startswith("# ColHeaders"):
            start_processing = True
            continue
        if start_processing and line.strip() != "":
            parts = line.strip().split()
            struct_name = parts[4]
            volume_mm3 = parts[3]
            data[struct_name + "_mm3_fastsurfer"] = volume_mm3
    return data

def generate_csv(data, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write headers as separate columns
        writer.writerow(data.keys())
        # Write values as separate columns
        writer.writerow(data.values())

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
