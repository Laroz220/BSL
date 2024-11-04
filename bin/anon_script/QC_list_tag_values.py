import os
import pydicom
import argparse
from pydicom.datadict import keyword_for_tag

def get_tag_name(tag):
    """Get the name of the tag based on its group and element."""
    try:
        return keyword_for_tag(tag)  # Get the tag name from the tag
    except KeyError:
        return 'Unknown Tag'

def list_dicom_tags_with_values(input_dir, output_file):
    if not os.path.isdir(input_dir):
        raise FileNotFoundError(f"Input directory {input_dir} does not exist.")
    
    print(f"Processing files in directory: {input_dir}")

    tags_info = {}  # To store tag names and their values

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                print(f"Processing file: {file_path}")
                dicom = pydicom.dcmread(file_path)
                
                # Add tag names and their values to the dictionary
                for tag in dicom.keys():
                    element = dicom.get(tag)
                    tag_name = get_tag_name(tag)  # Get the tag name
                    tag_value = element.value if element.value is not None else "NA"
                    
                    # Append values to the existing tag name or create a new entry
                    if tag_name in tags_info:
                        tags_info[tag_name].append(tag_value)
                    else:
                        tags_info[tag_name] = [tag_value]
                    
            except Exception as e:
                print(f"Failed to process {file_path}: {e}")

    # Write tag names and their values to the output file
    try:
        with open(output_file, 'w') as out_file:
            for tag_name, tag_values in sorted(tags_info.items()):  # Sorted to list in alphabetical order
                out_file.write(f"{tag_name}: {', '.join(tag_values)}\n")
        print(f"Tag list with values saved to {output_file}")
    except Exception as e:
        print(f"Failed to write output file {output_file}: {e}")

def main():
    parser = argparse.ArgumentParser(description="List DICOM tag names and their values from files in a specified directory.")
    
    parser.add_argument('input_directory', type=str, help="Path to the directory containing DICOM files.")
    parser.add_argument('output_file', type=str, help="Path to the file where tag names and values will be saved.")
    
    args = parser.parse_args()
    
    # Check if input directory exists
    if not os.path.exists(args.input_directory):
        print(f"Error: Input directory {args.input_directory} does not exist.")
        return
    
    # Run the tag listing
    list_dicom_tags_with_values(args.input_directory, args.output_file)

if __name__ == "__main__":
    main()
