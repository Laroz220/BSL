import os
import argparse
import pydicom
import warnings
from pydicom.uid import JPEG2000, JPEG2000Lossless, RLELossless, ExplicitVRLittleEndian, ExplicitVRBigEndian, ImplicitVRLittleEndian

# Suppress pydicom warnings
warnings.simplefilter("ignore", UserWarning)

# List of compressed transfer syntaxes to decompress
COMPRESSED_SYNTAXES = {JPEG2000, JPEG2000Lossless, RLELossless}

# List of uncompressed transfer syntaxes to skip
UNCOMPRESSED_SYNTAXES = {ExplicitVRLittleEndian, ExplicitVRBigEndian, ImplicitVRLittleEndian}

# Function to decompress DICOM files
def decompress_dicom(input_dir):
    decompressed_count = 0
    skipped_count = 0
    total_files = 0

    #print(f"   --> {input_dir}..")  # Print before processing starts

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if not filename.endswith(".dcm"):
                continue  # Skip non-DICOM files
            
            input_path = os.path.join(root, filename)
            total_files += 1

            try:
                ds = pydicom.dcmread(input_path)

                # Check Transfer Syntax UID to determine if decompression is needed
                transfer_syntax = ds.file_meta.TransferSyntaxUID

                if transfer_syntax in UNCOMPRESSED_SYNTAXES:
                    skipped_count += 1
                    continue  # Skip already uncompressed files

                if transfer_syntax in COMPRESSED_SYNTAXES:
                    try:
                        ds.decompress()  # Decompress the pixel data
                        ds.save_as(input_path)  # Overwrite the original file
                        decompressed_count += 1
                    except Exception:
                        skipped_count += 1
                else:
                    skipped_count += 1  # Skip unsupported compression formats

            except Exception:
                skipped_count += 1  # Skip files with processing errors

    # Print final summary for the folder
    print(f"Processed folder: {input_dir}")
    print(f"  - Total DICOM files: {total_files}")
    print(f"  - Decompressed: {decompressed_count}")
    print(f"  - Skipped: {skipped_count}\n")

# Main function with argparse
def main():
    parser = argparse.ArgumentParser(description="Decompress JPEG 2000 or RLE compressed DICOM files.")
    parser.add_argument(
        "-i", "--input", required=True, nargs="+", help="Path(s) to input directory containing DICOM files."
    )
    args = parser.parse_args()

    for input_folder in args.input:
        if os.path.isdir(input_folder):
            decompress_dicom(input_folder)
        else:
            print(f"Error: '{input_folder}' is not a valid directory.")

if __name__ == "__main__":
    main()
