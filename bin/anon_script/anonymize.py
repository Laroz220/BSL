import os
import pydicom
import argparse
from tqdm import tqdm  # Import tqdm for progress bar

def anonymize_dicom(input_file, output_file, study_id_value):
    try:
        # Load the DICOM file
        dicom = pydicom.dcmread(input_file)

        # Define the tags to remove
        tags_to_remove = [
            (0x0040, 0x0555), (0x0040, 0x4035), (0x0038, 0x0010), (0x4000, 0x0010),
            (0x0040, 0xa078), (0x0010, 0x1081), (0x0040, 0x3001), (0x0070, 0x0086),
            (0x0008, 0x2111), (0x0010, 0x2150), (0x0038, 0x0300), (0x0040, 0xa07c),
            (0xfffc, 0xfffc), (0x0010, 0x2154), (0x0010, 0x0101), (0x0010, 0x0102),
            (0x0010, 0x21f0), (0x0040, 0x1004), (0x0040, 0x0243), (0x0008, 0x1052),
            (0x0008, 0x1050), (0x0040, 0x1102), (0x0040, 0x1101), (0x0040, 0xa123),
            (0x0040, 0x1103), (0x4008, 0x0114), (0x0008, 0x1048), (0x0008, 0x1049),
            (0x0008, 0x1062), (0x0010, 0x2299), (0x0010, 0x2297), (0x4008, 0x0118),
            (0x4008, 0x0042), (0x300e, 0x0008), (0x0040, 0x4034), (0x0038, 0x001e),
            (0x0040, 0x000b), (0x0040, 0x0006), (0x0008, 0x1010), (0x0008, 0x2112),
            (0x0038, 0x0060), (0x0013, 0x1013), (0x0010, 0x1005), (0x0010, 0x0032),
            (0x0010, 0x1060), (0x0010, 0x1001), (0x0010, 0x1002), (0x0010, 0x1000),
            (0x0040, 0x1001), (0x0040, 0x1005), (0x0032, 0x1032), (0x0032, 0x1033),
            (0x0040, 0x0275), (0x0010, 0x1030), (0x0032, 0x1070), (0x0008, 0x0021),
            (0x0040, 0x0012), (0x0008, 0x1195), (0x0013, 0x1011), (0x0040, 0xa124),
            (0x0040, 0xa088), (0x0040, 0xa073), (0x0040, 0xa027), (0x0038, 0x4000),
            (0x0010, 0x0020), (0x0010, 0x0010), (0x0040, 0xa123), (0x0010, 0x0030),
            (0x0008, 0x0090), (0x0070, 0x0084), (0x0020, 0x0010), (0x0040, 0xa075)
        ]

        # Define the tags to clear and set StudyID to the input directory name
        tags_to_clear = {
            (0x0040, 0xa123): "",  # PersonName - empty
            (0x0010, 0x0030): "",  # PatientBirthDate - empty
            (0x0008, 0x0090): "",  # ReferringPhysicianName - empty
            (0x0070, 0x0084): "",  # ContentCreatorsName - empty
            (0x0018, 0x1030): study_id_value,  # StudyID - set to input directory name
            (0x0040, 0xa075): "",  # VerifyingObserverName - empty
        }

        # Remove specified tags
        for tag in tags_to_remove:
            if tag in dicom:
                dicom.pop(tag, None)

        # Clear specified tags or set the StudyID
        for tag, value in tags_to_clear.items():
            if tag in dicom:
                dicom[tag].value = value

        # Save the anonymized DICOM file
        dicom.save_as(output_file)

    except Exception as e:
        # Log the error to a file
        with open('error_log.txt', 'a') as log_file:
            log_file.write(f"Failed to process {input_file}: {e}\n")

def anonymize_dicom_files_in_directory(input_dir, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Extract the name of the input directory
    study_id_value = os.path.basename(os.path.normpath(input_dir))

    # Gather all files to process
    all_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            input_file_path = os.path.join(root, file)
            all_files.append(input_file_path)

    # Initialize progress bar
    with tqdm(total=len(all_files), desc="Processing DICOM files") as pbar:
        # Process each file
        for input_file_path in all_files:
            # Construct the corresponding output path
            relative_path = os.path.relpath(input_file_path, input_dir)
            output_file_path = os.path.join(output_dir, relative_path)
            
            # Create the necessary directories in the output path
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            # Try to anonymize the DICOM file with the StudyID set to the input directory name
            anonymize_dicom(input_file_path, output_file_path, study_id_value)
            
            # Update progress bar
            pbar.update(1)

def main():
    parser = argparse.ArgumentParser(description="Anonymize DICOM files by removing specific tags and clearing others.")
    
    # Adding arguments
    parser.add_argument('input_directory', type=str, help="Path to the directory containing subject folders with DICOM files.")
    parser.add_argument('output_directory', type=str, help="Path to the directory where anonymized DICOM files will be saved.")
    
    # Parsing arguments
    args = parser.parse_args()
    
    # Check if input directory exists
    if not os.path.exists(args.input_directory):
        # Log the error to a file
        with open('error_log.txt', 'a') as log_file:
            log_file.write(f"Error: Input directory {args.input_directory} does not exist.\n")
        return
    
    # Run the anonymization
    anonymize_dicom_files_in_directory(args.input_directory, args.output_directory)

if __name__ == "__main__":
    main()
